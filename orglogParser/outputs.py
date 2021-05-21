from click import style

FLAG_COLORS = {
    'default_label': 'cyan',
    'default_val': 'green',
    'attention': 'red',
    'query': 'cyan'
}

def query(str):
    return label(str, flag='query')

def err_label(key, value):
    return label(key, value, flag='attention', all_one=True)

def label(key, value=None, flag=None, all_one=False):
    l_color, v_color = _set_color(flag, all_one)
    st_key = _styled_str(key, l_color)
    st_val = _styled_str(str(value), v_color)

    return st_key if flag == 'query' else f"{st_key}: {st_val}"

def _styled_str(str, color_flag):
    return style(str, fg=color_flag)

def _set_color(flag, all_one):
    try:
        l_color = FLAG_COLORS[flag]
        v_color = FLAG_COLORS[flag] if all_one else FLAG_COLORS['default_val']
    except:
        l_color = FLAG_COLORS['default_label']
        v_color = FLAG_COLORS['default_val']
    finally:
        return l_color, v_color
