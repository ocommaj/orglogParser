from click import style

def query(str):
    return label(str, flag='query')

def label(key, value=None, flag=None):
    if flag == 'query':
        return _styled_str(key, 'cyan')

    styled_key = _styled_str(f"{key}: ", 'cyan')
    styled_val = _styled_str(str(value), 'green')
    return f"{styled_key}{styled_val}"

def _styled_str(str, color_flag):
    return style(str, fg=color_flag)
