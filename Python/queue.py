class fila():
    def __init__(self):
        self.fila = []

    def insere(self, elemento):
        if (self.fila.count(elemento) == 0):
            self.fila.append(elemento)

    def get_fila(self):
        return self.fila
