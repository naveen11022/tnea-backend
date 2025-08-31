from mongoengine import connect, Document, IntField, StringField, FloatField

connect('tnea', host='127.0.0.1', port=27017)


class Allotment(Document):
    s_no = IntField(null=True)
    aggr_mark = FloatField()
    general_rank = StringField(max_length=10)
    community_rank = StringField(max_length=10)
    community = StringField(max_length=50)
    college_code = StringField(max_length=10)
    branch_code = StringField(max_length=10)
    allotted_category = StringField(max_length=50)
    year = IntField()
    round = StringField(max_length=10)

    meta = {
        'collection': 'allotment'
    }


class Branch(Document):
    branch_code = StringField(max_length=10, null=True)
    branch_name = StringField(max_length=300, null=True)

    meta = {
        'collection': 'branch'
    }


class Colleges(Document):
    s_no = IntField(null=True)
    college_code = IntField(primary_key=True)
    college_name = StringField(max_length=512, null=True)
    location = StringField(max_length=512, null=True)
    region = StringField(max_length=100, null=True)

    meta = {
        'collection': 'colleges'
    }
