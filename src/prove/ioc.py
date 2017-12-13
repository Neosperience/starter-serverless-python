#!/Library/Frameworks/Python.framework/Versions/3.3/bin/python3
# -*- coding: utf-8 -*-


class AbstractProvider:

    def __init__(self, object=None):
        self.object = object

    def __call__(self):
        if self.object is None:
            self.create_object()
        return self.object


class ObjectProvider(AbstractProvider):

    def __init__(self, object):
        AbstractProvider.__init__(self, object)


class SingletonProvider(AbstractProvider):

    def __init__(self, factory, **kwargs):
        AbstractProvider.__init__(self)
        self.factory = factory
        self.factory_providers = kwargs
        self.attributes_providers = {}
        self.injection_method_name = None
        self.injection_method_providers = {}

    def set_attributes_providers(self, **kwargs):
        self.attributes_providers = kwargs

    def set_injection_method_providers(self, injection_method_name, **kwargs):
        self.injection_method_name = injection_method_name
        self.injection_method_providers = kwargs

    def create_object(self):
        def providers_to_kwargs(providers):
            return {name: provider() for name, provider in providers.items()}
        self.object = self.factory(**providers_to_kwargs(self.factory_providers))
        for name, provider in self.attributes_providers.items():
            setattr(self.object, name, provider())
        if self.injection_method_name is not None:
            injection_method = getattr(self.object, self.injection_method_name)
            injection_method(**providers_to_kwargs(self.injection_method_providers))


if __name__ == '__main__':

    cfg = {'a': 1, 'b': True}

    class Service1:
        def __init__(self, config, service2=None):
            self.config = config
            self.service2 = service2

        def m1(self):
            print('Service1.m1()')
            self.service2.m2()

        def m2(self):
            print('Service1.m2(): config = ' + str(self.config))

    class Service2:
        def __init__(self, config, service1=None):
            self.config = config
            self.service1 = service1

        def m1(self):
            print('Service2.m1()')
            self.service1.m2()

        def m2(self):
            print('Service2.m2(): config = ' + str(self.config))

    def Service3(config, service1=None, service2=None):
        def s1m2():
            service1.m2()

        def s2m2():
            service2.m2()

        class Service:
            def m1(self):
                print('Service3.m1()')
                s1m2()
                s2m2()

            def m2(self):
                print('Service3.m2(): config = ' + str(config))

            def init(self, s1, s2):
                nonlocal service1, service2
                service1 = s1
                service2 = s2
        return Service()

    class Container:
        config = ObjectProvider(cfg)
        service1 = SingletonProvider(Service1, config=config)
        service2 = SingletonProvider(Service2, config=config)
        service3 = SingletonProvider(Service3, config=config)
        # service3 = SingletonProvider(Service3, config = config, service1 = service1, service2 = service2)

        service1.set_attributes_providers(service2=service2)
        service2.set_attributes_providers(service1=service1)
        service3.set_injection_method_providers('init', s1=service1, s2=service2)

    class Container2:
        def __init__(self):
            self.config = ObjectProvider(cfg)
            self.service1 = SingletonProvider(Service1, config=self.config)
            self.service2 = SingletonProvider(Service2, config=self.config)
            self.service3 = SingletonProvider(Service3, config=self.config)
            # self.service3 = SingletonProvider(Service3, config = config, service1 = service1, service2 = service2)

            self.service1.set_attributes_providers(service2=self.service2)
            self.service2.set_attributes_providers(service1=self.service1)
            self.service3.set_injection_method_providers('init', s1=self.service1, s2=self.service2)

    config = Container.config()
    service1 = Container.service1()
    service2 = Container.service2()
    service3 = Container.service3()

    service1.m1()
    service2.m1()
    service3.m1()
    service3.m2()

    print('=======')

    container = Container()

    config = container.config()
    service1 = container.service1()
    service2 = container.service2()
    service3 = container.service3()

    service1.m1()
    service2.m1()
    service3.m1()
    service3.m2()
