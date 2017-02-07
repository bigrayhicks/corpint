#!/usr/bin/env python
from flask import Blueprint, request, url_for, redirect
from flask import render_template, current_app

from corpint.integrate import train_judgement

blueprint = Blueprint('base', __name__)

SKIP_FIELDS = ['name', 'origin', 'fingerprint', 'uid']
JUDGEMENTS = {
    'TRUE': True,
    'FALSE': False,
    'NULL': None,
}


def common_fields(left, right):
    keys = set()
    for obj in [left, right]:
        for k, v in obj.items():
            if v is not None and k not in SKIP_FIELDS:
                keys.add(k)
    return list(sorted([k for k in keys]))


@blueprint.route('/', methods=['GET'])
def index():
    return redirect(url_for('.undecided_get'))


@blueprint.route('/undecided', methods=['GET'])
def undecided_get():
    """Retrieve two lists of possible equivalences to map."""
    pairs = current_app.deduper.uncertainPairs()
    candidates = []
    for (left, right) in pairs:
        candidate = {'left': left, 'right': right}
        candidate['fields'] = common_fields(left, right)
        candidate['height'] = len(candidate['fields']) + 2
        candidates.append(candidate)
    return render_template('undecided.html',
                           candidates=candidates)


@blueprint.route('/undecided', methods=['POST'])
def undecided_post():
    """Retrieve two lists of possible equivalences to map."""
    judgement = JUDGEMENTS.get(request.form.get('judgement'))
    left = request.form.get('left')
    right = request.form.get('right')
    current_app.project.emit_judgement(left, right, judgement)
    train_judgement(current_app.project, current_app.deduper,
                    left, right, judgement)
    return undecided_get()
