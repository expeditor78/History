# -*- coding: utf-8 -*-
"""Общие «кирпичики» для текстов тем."""

def T(*rows, head=None):
    h = ''
    if head:
        h = '<thead><tr>' + ''.join(f'<th>{c}</th>' for c in head) + '</tr></thead>'
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table>{h}<tbody>{b}</tbody></table></div>'

def EX(*items):
    return '<ul class="ex">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

def RULE(t):
    return f'<div class="rule"><b>📌 Правило.</b> {t}</div>'

def WARN(t):
    return f'<div class="warn"><b>⚠️ Частая ошибка.</b> {t}</div>'

def SAY(t):
    return f'<div class="say"><b>💬 Простыми словами</b><p>{t}</p></div>'

def TIP(t):
    return f'<div class="tip"><b>💡 Лайфхак.</b> {t}</div>'

def STEPS(title, *items):
    return f'<div class="stepsbox"><b>🪜 {title}</b><ol class="steps">' + ''.join(f'<li>{i}</li>' for i in items) + '</ol></div>'

def DEMO(title, *lines):
    return f'<div class="demo"><b>🔍 Разберём вместе: {title}</b><ul>' + ''.join(f'<li>{l}</li>' for l in lines) + '</ul></div>'

def ASK(q, a):
    return f'<details class="ask"><summary>🤔 {q}</summary><div>{a}</div></details>'

def RECAP(*items):
    return '<div class="recap"><b>✅ Главное запомнить</b><ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul></div>'

def Q(q, opts, a, expl):
    """a — индекс верного варианта (с 0)."""
    return dict(q=q, o=opts, a=a, e=expl)
