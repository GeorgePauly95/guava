def manage_connection(model_function):
    def inner(cls, *args, **kwargs):
        from engine import engine

        with engine.begin() as connection:
            return model_function(cls, connection, *args, **kwargs)

    return inner
