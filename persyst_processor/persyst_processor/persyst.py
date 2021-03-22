
def get_config_section(section, config):
    '''
    Helper funstion to parse Persyst layout files.

    Returns a dictionary that contains the data of the provided section
    using the layout file.
    '''

    section_dict = {}

    for option in config.options(section):
        try:
            section_dict[option] = config.get(section, option)
        except:
            raise TimeSeriesImportError(
                'Cannot get specified section and field in .lay file.',\
                 section=section, field=option)

    return section_dict

def scaled(num):
    '''
    Time scaling factor
    '''
    return long(1e6 * num)

def find_lay(config, files):
    for f in files:
        try:
            config.read(f)
            return f
        except:
            pass

# TODO: write better check for dat files
def find_dat(files):
    for f in files:
        if f.endswith('.dat') or f.endswith('.DAT'):
            return f
