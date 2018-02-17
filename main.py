from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import datetime
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False, default="")
    show = db.Column(db.String(100), nullable=False, default="")
    visitors = db.Column(db.Integer, nullable=False, default=0)
    vert = db.Column(db.String(50), nullable=False, default="")


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
        db.session.add(show)
    show.date = date
    show.time = time
    show.show = show_name
    show.visitors = visitors
    show.vert = vert
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
    # TODO: implement javascript
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
    while len(shows) < 10:
        shows.append(Show(id="", time="", show="", vert="", visitors=""))
    weekday = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"][date.weekday()]
    return render_template('index.html', date=date.strftime("%Y-%m-%d"), shows=shows, weekday=weekday)


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
    app.debug = True
    app.run()
