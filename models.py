from database import db

class Veiculos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return{
            'id': self.id,
            'descricao': self.descricao
        }


class Itens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    intervalo_km = db.Column(db.Integer, nullable=False)
    intervalo_prazo = db.Column(db.Integer, nullable=False)
    ultima_troca_km = db.Column(db.Integer, nullable=False)
    ultima_troca_data = db.Column(db.Date, nullable=False)
    veiculo = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    veiculo_relacionamento = db.relationship('Veiculos', backref=db.backref('itens', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'intervalo_km': self.intervalo_km,
            'intervalo_prazo': self.intervalo_prazo,
            'ultima_troca_km': self.ultima_troca_km,
            'ultima_troca_data': self.ultima_troca_data.isoformat(),
            'veiculo': self.veiculo,
        }