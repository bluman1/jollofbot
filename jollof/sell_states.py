sell_states = {
    'DEFAULT': ['1'],
    'CANCELLED': ['DEFAULT'],

    'REQUEST_CODE': ['REQUEST_CODE', 'CANCELLED'],
    
}


def is_seller_next_state(old_state, new_state):
    '''
    Returns boolean if new_state is a next state for old_state
    '''
    try:
        state = sell_states[old_state]
        if new_state in state:
            return True
        else:
            return False
    except KeyError:
        return False