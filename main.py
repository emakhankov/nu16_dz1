from flask import Flask, render_template, request, abort, redirect, url_for, send_file, jsonify
import service.VGTRKService as VGTRKService

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/contacts/")
def contacts():
    return render_template('contacts.html')


@app.route("/query/")
def query():
    return render_template('query.html')


@app.route("/result/", methods=['POST'])
def result():
    if request.form:
        num = request.form.get('num', '')
        name = request.form.get('name', '')

        if num != '':
            rows = VGTRKService.get_by_nomer(num)
        elif name != '':
            rows = VGTRKService.get_by_description(name)
        else:
            rows = []
        return render_template('result.html', rows=rows)
    else:
        abort(404)

@app.route("/api/")
def api():
    num = request.args.get('num', '')
    name = request.args.get('name', '')
    if num != '':
        rows = VGTRKService.get_by_nomer(num)
    elif name != '':
        rows = VGTRKService.get_by_description(name)
    else:
        rows = VGTRKService.get_by_description('')
    json = rows.reset_index().to_json(orient='records', force_ascii=False)
    return json

@app.route("/result/", methods=['GET'])
def result_get():
    return redirect(url_for('query'), code=303)


@app.route("/excel/", methods=['POST', 'GET'])
def excel():
    try:
        VGTRKService.verify_up_to_date()
        return send_file(VGTRKService.output_excel, attachment_filename='data.xlsx')
    except Exception as e:
        return str(e)



if __name__ == "__main__":
    app.run(host='0.0.0.0')
