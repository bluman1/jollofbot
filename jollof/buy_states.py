buy_states = {
    'DEFAULT': ['1'],
    'CANCELLED': ['DEFAULT'],

    'GET_LOCATION_JOLLOF': ['GET_LOCATION_JOLLOF', 'CANCELLED'],
    'GET_LOCATION_DELICACY': ['GET_LOCATION_DELICACY', 'CANCELLED'],
    'TALK_TO_JOLLOF': ['DEFAULT'],
    'ADMIN_TALKING': ['ADMIN_TALKING', 'DEFAULT'],

    'ORDER_JOLLOF': ['ORDER_JOLLOF', 'CANCELLED'],
    'JOLLOF_RESERVATION': ['JOLLOF_RESERVATION', 'CANCELLED'],
    'DELICACY_RESERVATION': ['DELICACY_RESERVATION', 'CANCELLED'],
    'VIEW_DELICACY_SELLERS': ['VIEW_DELICACY_SELLERS', 'ORDER_DELICACY'],
    'ORDER_DELICACY': ['ORDER_DELICACY', 'CANCELLED'],

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