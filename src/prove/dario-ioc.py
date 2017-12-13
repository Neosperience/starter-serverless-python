#!/usr/bin/python
# -*- coding: utf-8 -*-

import dependency_injector.containers as containers
import dependency_injector.providers as providers


class Service1:
    def m1(self):
        print('Service1.m1()')
        self.service2.m2()

    def m2(self):
        print('Service1.m2(): config = ' + str(self.config))


class Service2:
    def m1(self):
        print('Service2.m1()')
        self.service1.m2()

    def m2(self):
        print('Service2.m2(): config = ' + str(self.config))


cfg = {'a': 1, 'b': True}


# non capisco come fanno i provider a mettersi via un riferimento al container, che dovranno usare
# per risolvere le dipendenze
class Container(containers.DeclarativeContainer):
    config = providers.Object(cfg)
    service1 = providers.Singleton(Service1)
    service2 = providers.Singleton(Service2)
    # chiamando questi metodi dopo aver definito i provider è possibile dichiarare le dipendenze incrociate:
    service1.set_attributes(config=config, service2=service2)
    # peccato però che così va in loop quando chiamo service1() o service2():
    # service2.set_attributes(config = config, service1 = service1)
    # e sono costretto a fare così...
    service2.set_attributes(config=config)


service1 = Container.service1()
service2 = Container.service2()
# e poi così...
service2.service1 = service1

service1.m1()
service2.m1()

# e allora vaffanculo, lo riscrivo io
