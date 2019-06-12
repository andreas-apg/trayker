class fila():
    def __init__(self):
        self.fila = []

    def insere(self, elemento):
        if (self.fila.count(elemento) == 0):
            self.fila.append(elemento)

    def remove(self, elemento):
        if (self.fila.count(elemento) > 0):
            self.fila.remove(elemento)

    def presente(self, elemento):
        if(self.fila.count(elemento) > 0):
            return True
        else:
            return False

    def pop(self):
        if(len(self.fila) > 0):
            return self.fila.pop(0)
        else:
            print('Fila vazia.')

    def get_fila(self):
        return self.fila
