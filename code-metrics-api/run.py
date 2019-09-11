from src import app
#app.run(host='0.0.0.0', port=app.config['PORT'] , ssl_context='adhoc', debug=True)
app.run(host='0.0.0.0',port=app.config['PORT'],debug=True)