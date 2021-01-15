from searcher import Searcher
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
searcher = Searcher('pic_index')

@app.route('/', methods=['POST', 'GET'])
def searcher_form():
    if request.method == "POST":
        # pass all the argument of request.form to the page result.
        return redirect(url_for('result', **request.form))
    return render_template("index.html")


@app.route('/result', methods=['GET'])
def result():
    # retrieve the arguments and get the results corresponding to the 
    # arguments from the searcher.

    request_dict = request.args.to_dict()
    results = searcher.query(request_dict)
    len_res = len(results)
    
    #render result.html.
    return render_template("result.html", **request_dict, results=results, len_res=len_res)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
