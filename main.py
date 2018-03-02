from flask import Flask, render_template, request, jsonify, make_response, send_file
import datetime
from collections import defaultdict
from models import db, Show
import pandas as pd
from io import BytesIO
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route("/add_row", methods=['POST', ])
def add_row():
    rowid = request.form.get('rowid')
    date = request.form.get('date')
    time = request.form.get('time')
    show_name = request.form.get('show_name')
    visitors = request.form.get('visitors')
    vert = request.form.get('vert')
    if any(field is None for field in [rowid, date, time, show_name, visitors, vert]) is None:
        return make_response(jsonify({'error': 'All fields are empty'}), 500)
    if all(field in [0, ''] for field in [visitors, time, show_name]):
        return make_response(jsonify({'error': 'Not enough fields'}), 500)
    print(rowid, date, time, show_name, visitors, vert)
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return '', 500
    show = Show.query.filter_by(id=rowid).first()
    if show is None:
        print("Creating new show")
        show = Show()
        try:
            show.id = int(rowid)
        except ValueError:
            pass
        db.session.add(show)
    if visitors == "":
        visitors = "0"
    try:
        visitors = int(visitors.strip())
    except ValueError:
        return make_response(jsonify({'error': 'Visitors must be a number'}))
    time = time.strip()
    if time.isnumeric() and len(time) == 4:
        time = time[:2] + ":" + time[2:]
    elif time.find(':') == 1:
        time = '0' + time
    show.date = date
    show.time = time.strip()
    show.show = show_name.strip()
    show.visitors = visitors
    show.vert = vert.strip()
    db.session.commit()

    ret = jsonify({"rowid": show.id,
                   "date": date.strftime("%Y-%m-%d"),
                   "time": time,
                   "show_name": show_name,
                   "visitors": visitors,
                   "vert": vert})
    return ret


@app.route("/delete_row", methods=["POST", ])
def delete_row():
    rowid = request.form.get("rowid")
    row = Show.query.filter_by(id=rowid).first()
    if row is None:
        return jsonify({'status': 'success'})  # Not in db, so already deleted
    db.session.delete(row)
    db.session.commit()
    return jsonify({'status': 'success'})


@app.route("/")
def index():
    return list_show(datetime.date.today())


@app.route("/<int:year>/<int:month>/<int:day>")
def view_list_show(year, month, day):
    try:
        date = datetime.date(year, month, day)
    except ValueError:
        return "Ikke en korrekt dato"
    return list_show(date)


def list_show(date: datetime.date):
    shows = list(Show.query.filter_by(date=date).order_by(Show.time))
    tmp_ids = set(show.id for show in shows)
    while len(shows) < 10:
        while True:
            tmp_id= (date - datetime.date(1991, 8, 9)).days*1000 + random.randint(0,999)
            if tmp_id not in tmp_ids:
                break;
        tmp_ids.add(tmp_id)
        shows.append(Show(id=str(tmp_id), time="", show="", vert="", visitors=""))
    weekday = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"][date.weekday()]
    prev_day_url = "/" + (date - datetime.timedelta(1)).strftime("%Y/%m/%d")
    next_day_url = "/" + (date + datetime.timedelta(1)).strftime("%Y/%m/%d")
    show_set = {show.show for show in Show.query.distinct(Show.show)}
    host_set = {show.vert for show in Show.query.distinct(Show.vert)}
    datalists = {'shows': show_set,
                 'hosts': host_set}
    return render_template('index.html', date=date.strftime("%Y-%m-%d"),
                           shows=shows, weekday=weekday,
                           prev_day=prev_day_url,
                           next_day=next_day_url,
                           datalists=datalists,
                           )


@app.route('/stats.xlsx')
def stats_xlsx():
    q = db.session.query(Show).order_by(Show.date, Show.time).all()
    cols = ["date", "time", "show", "visitors", "vert"]
    df = pd.DataFrame([[getattr(row, c) for c in cols] for row in q], columns=cols)
    bio = BytesIO()

    writer = pd.ExcelWriter(bio)
    df.to_excel(writer, "stats", index=False)
    sheet = writer.sheets['stats']
    sheet.auto_filter.ref = 'A:E'
    writer.save()
    bio.seek(0)
    return send_file(bio, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



@app.route('/stats/day')
def stats_day():
    q = db.session.query(Show.date, db.func.sum(Show.visitors), db.func.avg(Show.visitors)).group_by(Show.date).all()
    return "<br>".join(f"{date} - Sum: {visitors:.0f} Avg: {avg:.1f}" for date, visitors, avg in q)


@app.route('/stats/month')
def stats_month():
    q = db.session.query(Show.date, db.func.sum(Show.visitors)).group_by(Show.date).all()
    month_stats = defaultdict(int)
    for date, visitors in q:
        month_stats[(date.year, date.month)] += visitors
    sorted_stats = [(key, month_stats[key]) for key in sorted(month_stats.keys())]
    return "<br>".join(f"{year}-{month}: {visitors}" for (year, month), visitors in sorted_stats)






if __name__ == "__main__":
    # db.create_all()
    # app.debug = True
    app.run(host="0.0.0.0")
