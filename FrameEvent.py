import inspect
#import ipdb


# class that handles generic events and delegation
# TODO: implement signature checking between Event signature and handler
# signature
import pdb
class Event_(object):

    # initialization function
    def __init__(self, **signature):
        '''
        Event_ as of now only accepts keyworded arguments
        Does not accept positional arguments for now: TODO
        '''
        self._signature = signature
        self._argnames = set(signature.keys())
        self._handlers = []

    # destructor function
    def __del__(self):
        self._argnames = None
        self._handlers = None
        self._signature = None

    # returns the signature of the event in string format
    def _kwargs_str(self):
        return ", ".join(k + "=" + v.__name__ for k, v in self._signature.items())

    # overloading the increment operator--> +=
    def __iadd__(self, handler):
        params = inspect.signature(handler).parameters
        valid = True
        argnames = set(n for n in params.keys())
        if argnames != self._argnames:
            valid = False
        for p in params.values():
            if p.kind == p.VAR_KEYWORD:
                valid = True
                break
            if p.kind not in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY):
                valid = False
                break
        if not valid:
            raise ValueError("Listener must have these arguments: (%s)"
                             % self._kwargs_str())
        self._handlers.append(handler)
        return self

    # overloading the decrement operator--> -=
    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    # overloading the function call operator--> ()
    def __call__(self, *args, **kwargs):
        if args or set(kwargs.keys()) != self._argnames:
            pdb.set_trace() # BREAKPOINT
            raise ValueError("This EventHook must be called with these " +
                             "keyword arguments: (%s)" % self._kwargs_str())
        for handler in self._handlers[:]:
            handler(**kwargs)

    # returns the event signature
    def __repr__(self):
        return "EventHook(%s)" % self._kwargs_str()

    # property that retrieves if any handlers have subscribed to the event
    @property
    def isSubscribed(self):
        return True if len(self._handlers) != 0 else False


def main():
    # script to test the event mechanism
    def print_1(name):
        print("printed by print_1 " + str(name))

    def print_2(name):
        print("printed by print_2 " + str(name))

    def print_3(name):
        print("printed by print_3 " + str(name))

    something = [1.0, 2.0, 3.0, 4.0, 5.0, 6.45768]  # "Neuken in the Keuken"
    something2 = 6
    # _event = Event(name=str)
    _event = Event_(name=None)

    _event += print_1
    _event += print_2
    _event += print_3

    print(_event.isSubscribed)
    _event(name=something)
    print(_event._kwargs_str())

    return None


if __name__ == "__main__":
    main()

