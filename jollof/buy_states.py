buy_states = {
    'DEFAULT': ['1'],
    'CANCELLED': ['DEFAULT'],

    'GET_LOCATION': ['GET_LOCATION', 'CANCELLED'],
    'TALK_TO_JOLLOF': ['DEFAULT'],
}


def is_buyer_next_state(old_state, new_state):
    '''
    Returns boolean if new_state is a next state for old_state
    '''
    try:
        state = buy_states[old_state]
        if new_state in state:
            return True
        else:
            return False
    except KeyError:
        return False