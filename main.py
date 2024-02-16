from twisted.internet import endpoints, reactor
from src.manager import ManagerFactory

endpoints.serverFromString(reactor, "tcp:25565").listen(ManagerFactory())
reactor.run()
