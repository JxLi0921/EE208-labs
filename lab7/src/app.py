ITEM_PER_PAGE = 8

from searcher import Searcher
import copy
import json
from flask import Flask, redirect, render_template, request, url_for, jsonify

app = Flask(__name__)
searcher = Searcher('pic_index')

@app.route('/', methods=['POST', 'GET'])
def searcher_form():
    if request.method == "POST":
        # pass all the argument of request.form to the page result.
        return redirect(url_for('result', **request.form, search_type='N', page=1))
    return render_template("index.html")

@app.route('/F-searcher', methods=["POST", "GET"])
def f_searcher_form():
    if request.method == "POST":
        # pass all the argument of request.form to the page result.
        return redirect(url_for('result', **request.form, search_type='F', page=1))
    return render_template("F_searcher.html")

@app.route('/result', methods=['GET'])
def result():
    # retrieve the arguments and get the results corresponding to the 
    # arguments from the searcher.

    request_dict = request.args.to_dict()
    H_checked = 'H-search' in request_dict
    p_checked = 'pic-search' in request_dict
    results = searcher.query(copy.copy(request_dict), H_checked, p_checked)

    total_item_num = len(results)
    end_page = total_item_num // ITEM_PER_PAGE + 1
    if total_item_num % ITEM_PER_PAGE == 0:
        end_page -= 1
    start_page = int(request_dict['page'])
    cutted_results = []
    if results:
        cutted_results = results[(start_page-1) * ITEM_PER_PAGE: 
                                 min(len(results), start_page * ITEM_PER_PAGE)]

    # raise ValueError
    #render result.html.
    return render_template("result.html", 
                           **request_dict,
                           results=cutted_results, 
                           len_res=len(results), 
                           H_checked=H_checked, 
                           p_checked=p_checked,
                           start=start_page,
                           end=end_page)

if __name__ == '__main__':
    app.run(debug=True, port=8080)