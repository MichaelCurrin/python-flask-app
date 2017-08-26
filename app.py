#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on 16 Dec 2016

A Python 2.7 app built with Flask.
It provides an API service from a SQLite3 database
Where a home page gives the user links to suggested endpoints
And where queried endpoints retrieve data from SQL and return as JSON.
"""
__author__ = '@MichaelCurrin'

from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine


class Type_Meta(Resource):
    
    def get(self):
        """
        This returns a uniiue list of post types available, so they can
        be used in a filtered posts URL if necessary.
        """
        connection = e.connect()
        query = connection.execute('SELECT * FROM vw_post_types;')

        # Note: use i[0] to have list of strings instead of list of lists
        data = [i[0] for i in query.cursor.fetchall()]

        result = {'Types':data}
        return jsonify(result)

    
class Summary(Resource):
    
    def get(self):
        """
        This returns summary data for all time, by Page ID
        """
        connection = e.connect()

        query = connection.execute("""SELECT `Page_ID`,
                                        COUNT(*) AS 'Posts',
                                        SUM(`Likes`) AS 'Total_Likes',
                                        SUM(`Comments`) AS 'Total_Comments',
                                        SUM(`Shares`) AS 'Total_Shares'
                                     FROM vw_posts
                                     GROUP BY `Page_ID`;""")
        data = [dict(zip(tuple(query.keys()), i)) for i in query.cursor]
        result = {'Summary':data}
        return jsonify(result)

    
class Posts_By_Type(Resource):
    
    def get(self, post_type):
        """
        This returns detailed post data but only for the type specified
        e.g. 'video'
        """
        connection = e.connect()
        query_str = 'SELECT * FROM vw_posts WHERE `Type`="%s";' % post_type
        query = connection.execute(query_str)
        data = [dict(zip(tuple (query.keys()), i)) for i in query.cursor]
        result = {'Posts':data}
        return jsonify(result)

    
class Posts_With_Filters(Resource):
    
    def get(self):
        """
        Returns actual posts, with filters applied if any
        """
        # set parameters from ?since=XXX&until=XXX&grouping=XXX
        # default to None
        since = request.args.get('since')
        until = request.args.get('until')
        grouping = request.args.get('grouping')

        # check for optional value of 'grouping=day' and apply to query
        if grouping=='day':
            tb_name = 'vw_daily'
            out_key = 'Days'
        else:
            tb_name = 'vw_posts'
            out_key = 'Posts'

        connection = e.connect()

        query_str = 'SELECT * FROM %s' % tb_name

        # insert dates if range specified
        if since and until:
            date_str = " WHERE `Date`>='%s' AND `Date`<='%s'" % (since, until)
            query_str = query_str + date_str

        query = connection.execute(query_str)
        data = [dict(zip(tuple (query.keys()), i)) for i in query.cursor]

        # use *out_key* to describe data as 'Days' or 'Posts'
        result = {out_key:data, 'Count':len(data)}
        return jsonify(result)

"""
# this gave an error not sufficient permissions
# further testing required

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down'
"""

# Create an engine for connecting to SQLite3.
db_name = 'social.db'
e = create_engine('sqlite:///%s' % db_name)

# create Flask app, with /static as path for html etc. files
app = Flask(__name__, static_url_path='/static')
# Create API
api = Api(app)

# Add home index page
@app.route('/')
def root():
    return app.send_static_file('index.html')

# Add API pages
api.add_resource(Summary, '/summary')
api.add_resource(Type_Meta, '/types')
api.add_resource(Posts_With_Filters, '/posts')
api.add_resource(Posts_By_Type, '/posts/<string:post_type>')


if __name__ == '__main__':
    # host='0.0.0.0'
    # host = '127.0.0.1' (default)
    app.run(port=5000, debug=True)
