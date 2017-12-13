#!/Library/Frameworks/Python.framework/Versions/3.3/bin/python3
# -*- coding: utf-8 -*-


def getAtPath(obj, path):
    print(obj, path)
    if isinstance(path, str):
        path = path.split('.')
    for step in path:
        if not isinstance(obj, list) and not isinstance(obj, dict):
            obj = None
            break
        obj = obj.get(step)
        if obj is None:
            break
    return obj


obj = {
    'uno': {
        'due': 'ciao'
    }
}

# print getAtPath(obj, [])
# print getAtPath(obj, ['nessuno'])
# print getAtPath(obj, ['uno'])
# print getAtPath(obj, ['uno', 'nessuno'])
# print getAtPath(obj, 'uno.due')
# print getAtPath(obj, ['uno', 'due', 'nessuno'])
# print getAtPath(3, ['uno', 'due', 'nessuno'])
# print getAtPath(['a', {'miao': 3}], [0])


class Service1:
    def service(self, a):
        print('Service 1: %s' % a)


class Service2:
    def service(self, a):
        print('Service 2: %s' % a)


# Così assomiglia a quello che faccio con javascript: si usano le variabili e le funzioni locali
# che non vengno viste all'esterno, dove arriva solo l'istanza con gli attributi che servono, ma
# spesso nessun attributo, visto che i metodi non sono attributi come gli altri perché sono dentro la
# classe e non nella function come in javascript. Infatti in questo caso __dict__ è vuoto.
def C(dep1=None, dep2=None):  # posso passare i servizi qui oppure iniettarli dopo con init()
    localvar = 10

    def localfun1(a):
        dep1.service(a)

    def localfun2(a):
        dep2.service(a)

    class Class:
        def m1(self, a):
            localfun1(a)

        def m2(self, a):
            localfun2(a)

        def inc(self):
            nonlocal localvar  # solo python 3
            localvar += 1
            print(localvar)

        def init(self, d1, d2):
            nonlocal dep1, dep2
            dep1 = d1
            dep2 = d2

    return Class()


c = C(Service1(), Service2())
print(c.__dict__)
c.m1(3)
c.m2(4)
c.inc()

c = C()
c.init(Service1(), Service2())
print(c.__dict__)
c.m1(3)
c.m2(4)
c.inc()


# Questa è la versione senza factory, più semplice, in cui tutto è attributo e metodo e visibile.
# Non mi piace perché espone inutilmente helper1(), helper2(). Non è un problema di robustezza,
# ma di interfaccia inutilmente affollata. Probabilmente però in Python è una cosa del tutto
# accettabile.
class C:
    def __init__(self, dep1, dep2):
        self.dep1 = dep1
        self.dep2 = dep2
        self.attr = 10

    def helper1(self, a):
        self.dep1.service(a)

    def helper2(self, a):
        self.dep2.service(a)

    def m1(self, a):
        self.helper1(a)

    def m2(self, a):
        self.helper2(a)

    def inc(self):
        self.attr += 1
        print(self.attr)


c = C(Service1(), Service2())
print(c.__dict__)
c.m1(3)
c.m2(4)
c.inc()
print(c.__dict__)
