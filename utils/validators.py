def validate_inputs(*args):
    return all(arg and arg.strip() for arg in args)
