# from momoapp import create_app

# app = create_app()
from momoapp import app

if __name__ =='__main__':
	app.run(host='0.0.0.0',debug=True)
#    app.run(debug= True)
