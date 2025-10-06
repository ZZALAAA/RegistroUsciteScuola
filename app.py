from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from tinydb import TinyDB, Query
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'classexit_secret_key'

# Database setup
db = TinyDB('database.json')
classi_table = db.table('classi')
alunni_table = db.table('alunni')
uscite_table = db.table('uscite')

Class = Query()
Alunno = Query()
Uscita = Query()

@app.route('/')
def index():
    """Homepage - visualizza tutte le classi"""
    classi = classi_table.all()
    return render_template('index.html', classi=classi)

@app.route('/classe/<classe_id>')
def visualizza_classe(classe_id):
    """Visualizza la dashboard di una classe specifica"""
    try:
        classe_id = int(classe_id)
        classe = classi_table.get(doc_id=classe_id)
        if not classe:
            flash('Classe non trovata', 'error')
            return redirect(url_for('index'))
        
        # Ottieni tutti gli alunni della classe
        alunni = alunni_table.search(Alunno.classe_id == classe_id)
        
        # Per ogni alunno, determina il suo stato attuale
        alunni_con_stato = []
        for alunno in alunni:
            # Trova l'ultima uscita dell'alunno
            ultima_uscita = uscite_table.search(
                (Uscita.alunno_id == alunno.doc_id) & (Uscita.ora_rientro == None)
            )
            
            # Trova l'ultima attività (uscita o rientro)
            tutte_uscite = uscite_table.search(Uscita.alunno_id == alunno.doc_id)
            ultima_attivita = None
            if tutte_uscite:
                ultima_attivita = max(tutte_uscite, key=lambda x: x['ora_uscita'])
            
            alunno_info = {
                'id': alunno.doc_id,
                'nome': alunno['nome'],
                'cognome': alunno['cognome'],
                'fuori_aula': len(ultima_uscita) > 0,
                'ultima_attivita': ultima_attivita
            }
            alunni_con_stato.append(alunno_info)
        
        # Controlla se c'è già qualcuno fuori
        qualcuno_fuori = any(a['fuori_aula'] for a in alunni_con_stato)
        
        return render_template('classe.html', 
                             classe=classe, 
                             alunni=alunni_con_stato,
                             qualcuno_fuori=qualcuno_fuori)
    except ValueError:
        flash('ID classe non valido', 'error')
        return redirect(url_for('index'))

@app.route('/nuova_classe', methods=['POST'])
def nuova_classe():
    """Crea una nuova classe"""
    nome_classe = request.form.get('nome_classe', '').strip()
    
    if not nome_classe:
        flash('Il nome della classe è obbligatorio', 'error')
        return redirect(url_for('index'))
    
    # Controlla se esiste già una classe con questo nome
    if classi_table.search(Class.nome == nome_classe):
        flash('Esiste già una classe con questo nome', 'error')
        return redirect(url_for('index'))
    
    classi_table.insert({
        'nome': nome_classe,
        'data_creazione': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    flash(f'Classe "{nome_classe}" creata con successo!', 'success')
    return redirect(url_for('index'))

@app.route('/aggiungi_alunno/<classe_id>', methods=['POST'])
def aggiungi_alunno(classe_id):
    """Aggiungi un nuovo alunno alla classe"""
    try:
        classe_id = int(classe_id)
        nome = request.form.get('nome', '').strip()
        cognome = request.form.get('cognome', '').strip()
        
        if not nome or not cognome:
            flash('Nome e cognome sono obbligatori', 'error')
            return redirect(url_for('visualizza_classe', classe_id=classe_id))
        
        # Controlla se l'alunno esiste già in questa classe
        if alunni_table.search((Alunno.classe_id == classe_id) & 
                              (Alunno.nome == nome) & 
                              (Alunno.cognome == cognome)):
            flash('Questo alunno è già presente nella classe', 'error')
            return redirect(url_for('visualizza_classe', classe_id=classe_id))
        
        alunni_table.insert({
            'nome': nome,
            'cognome': cognome,
            'classe_id': classe_id,
            'data_inserimento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        flash(f'Alunno {nome} {cognome} aggiunto con successo!', 'success')
        return redirect(url_for('visualizza_classe', classe_id=classe_id))
        
    except ValueError:
        flash('ID classe non valido', 'error')
        return redirect(url_for('index'))

@app.route('/registra_uscita/<alunno_id>', methods=['POST'])
def registra_uscita(alunno_id):
    """Registra l'uscita di un alunno"""
    try:
        alunno_id = int(alunno_id)
        alunno = alunni_table.get(doc_id=alunno_id)
        
        if not alunno:
            flash('Alunno non trovato', 'error')
            return redirect(url_for('index'))
        
        # Controlla se l'alunno è già fuori
        uscita_attiva = uscite_table.search(
            (Uscita.alunno_id == alunno_id) & (Uscita.ora_rientro == None)
        )
        
        if uscita_attiva:
            flash(f'{alunno["nome"]} {alunno["cognome"]} è già fuori dall\'aula', 'error')
            return redirect(url_for('visualizza_classe', classe_id=alunno['classe_id']))
        
        # Controlla se c'è già qualcuno fuori dalla classe
        alunni_classe = alunni_table.search(Alunno.classe_id == alunno['classe_id'])
        for a in alunni_classe:
            uscite_attive = uscite_table.search(
                (Uscita.alunno_id == a.doc_id) & (Uscita.ora_rientro == None)
            )
            if uscite_attive:
                flash('C\'è già un alunno fuori dall\'aula. Attendere il suo rientro.', 'error')
                return redirect(url_for('visualizza_classe', classe_id=alunno['classe_id']))
        
        # Registra l'uscita
        now = datetime.now()
        uscite_table.insert({
            'alunno_id': alunno_id,
            'classe_id': alunno['classe_id'],
            'ora_uscita': now.strftime('%Y-%m-%d %H:%M:%S'),
            'ora_rientro': None
        })
        
        flash(f'{alunno["nome"]} {alunno["cognome"]} è uscito dall\'aula alle {now.strftime("%H:%M")}', 'success')
        return redirect(url_for('visualizza_classe', classe_id=alunno['classe_id']))
        
    except ValueError:
        flash('ID alunno non valido', 'error')
        return redirect(url_for('index'))

@app.route('/registra_rientro/<alunno_id>', methods=['POST'])
def registra_rientro(alunno_id):
    """Registra il rientro di un alunno"""
    try:
        alunno_id = int(alunno_id)
        alunno = alunni_table.get(doc_id=alunno_id)
        
        if not alunno:
            flash('Alunno non trovato', 'error')
            return redirect(url_for('index'))
        
        # Trova l'uscita attiva
        uscita_attiva = uscite_table.search(
            (Uscita.alunno_id == alunno_id) & (Uscita.ora_rientro == None)
        )
        
        if not uscita_attiva:
            flash(f'{alunno["nome"]} {alunno["cognome"]} non risulta fuori dall\'aula', 'error')
            return redirect(url_for('visualizza_classe', classe_id=alunno['classe_id']))
        
        # Registra il rientro
        now = datetime.now()
        uscite_table.update(
            {'ora_rientro': now.strftime('%Y-%m-%d %H:%M:%S')},
            doc_ids=[uscita_attiva[0].doc_id]
        )
        
        flash(f'{alunno["nome"]} {alunno["cognome"]} è rientrato in aula alle {now.strftime("%H:%M")}', 'success')
        return redirect(url_for('visualizza_classe', classe_id=alunno['classe_id']))
        
    except ValueError:
        flash('ID alunno non valido', 'error')
        return redirect(url_for('index'))

@app.route('/storico/<alunno_id>')
def storico_alunno(alunno_id):
    """Visualizza lo storico delle uscite di un alunno"""
    try:
        alunno_id = int(alunno_id)
        alunno = alunni_table.get(doc_id=alunno_id)
        
        if not alunno:
            flash('Alunno non trovato', 'error')
            return redirect(url_for('index'))
        
        classe = classi_table.get(doc_id=alunno['classe_id'])
        
        # Ottieni tutte le uscite dell'alunno, ordinate per data
        uscite = uscite_table.search(Uscita.alunno_id == alunno_id)
        uscite_ordinate = sorted(uscite, key=lambda x: x['ora_uscita'], reverse=True)
        
        return render_template('storico.html', 
                             alunno=alunno, 
                             classe=classe,
                             uscite=uscite_ordinate)
        
    except ValueError:
        flash('ID alunno non valido', 'error')
        return redirect(url_for('index'))

@app.route('/elimina_classe/<classe_id>', methods=['POST'])
def elimina_classe(classe_id):
    """Elimina una classe e tutti i suoi dati associati"""
    try:
        classe_id = int(classe_id)
        classe = classi_table.get(doc_id=classe_id)
        
        if not classe:
            flash('Classe non trovata', 'error')
            return redirect(url_for('index'))
        
        # Elimina tutte le uscite degli alunni della classe
        alunni_classe = alunni_table.search(Alunno.classe_id == classe_id)
        for alunno in alunni_classe:
            uscite_table.remove(Uscita.alunno_id == alunno.doc_id)
        
        # Elimina tutti gli alunni della classe
        alunni_table.remove(Alunno.classe_id == classe_id)
        
        # Elimina la classe
        classi_table.remove(doc_ids=[classe_id])
        
        flash(f'Classe "{classe["nome"]}" eliminata con successo', 'success')
        return redirect(url_for('index'))
        
    except ValueError:
        flash('ID classe non valido', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)