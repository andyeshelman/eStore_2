
def route(func):
    def wrapper():
        print('An HTTP request was made')
        request = {'data': {'username': 'brians', 'password': 'abc123'}}
        res = func(request)
        print('This is the response:', res)
    return wrapper


@route
def signup(new_user_data):
    print('This is our function!')
    new_user = {
        'id': 1,
        'username': new_user_data['data']['username'],
        'password': new_user_data['data']['password']
    }
    return new_user

#signup()

from faker import Faker

import faker_commerce

fake = Faker()
fake.add_provider(faker_commerce.Provider)

for _ in range(10):
    print(fake.ecommerce_name())