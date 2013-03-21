import flask
import hashlib
import json

json_mimetypes = ['application/json']


class Request(flask.Request):
    # from http://flask.pocoo.org/snippets/45/
    def wants_json(self):
        mimes = json_mimetypes
        mimes.append('text/html')
        best = self.accept_mimetypes.best_match(mimes)
        return best in json_mimetypes and \
            self.accept_mimetypes[best] > \
            self.accept_mimetypes['text/html']


def sign_vote(api_key, args):
    data = "ffu0" + api_key
    for k, v in sorted(args.items()):
        if k == 'sig':
            continue
        data += '{0}{1}'.format(k, v)
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()
