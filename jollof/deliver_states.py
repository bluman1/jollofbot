deliver_states = {
    'DEFAULT': ['1', 'PENDING_ORDERS', 'ACCEPT_PENDING_JOLLOF', 'ACCEPT_PENDING_DELICACY', 'TO_PICKUP', 'PICKED_UP_JOLLOF', 'PICKED_UP_DELICACY', 'TO_DROPOFF', 'DROPPED_OFF_JOLLOF', 'DROPPED_OFF_DELICACY'],
    'CANCELLED': ['DEFAULT'],

    'FLASH_LOCATION': ['FLASH_LOCATION', 'CANCELLED'],
    'REQUEST_PHONE': ['REQUEST_PHONE', 'CANCENCELLED'],

    'PENDING_ORDERS': ['PENDING_ORDERS', 'ACCEPT_PENDING_JOLLOF', 'ACCEPT_PENDING_DELICACY', 'CANCELLED'],
    
    'ACCEPT_PENDING_JOLLOF': ['ACCEPT_PENDING_JOLLOF', 'CANCELLED'],
    
    'ACCEPT_PENDING_DELICACY': ['ACCEPT_PENDING_DELICACY', 'CANCELLED'],
    
    'TO_PICKUP': ['TO_PICKUP', 'PICKED_UP_JOLLOF', 'PICKED_UP_DELICACY', 'CANCELLED'],

    'PICKED_UP_JOLLOF': ['PICKED_UP_JOLLOF', 'CANCELLED'],

    'PICKED_UP_DELICACY': ['PICKED_UP_DELICACY', 'CANCELLED'],

    'TO_DROPOFF': ['TO_DROPOFF', 'DROPPED_OFF_JOLLOF', 'DROPPED_OFF_DELICACY', 'CANCELLED'],

    'DROPPED_OFF_JOLLOF': ['DROPPED_OFF_JOLLOF', 'CANCELLED'],

    'DROPPED_OFF_DELICACY': ['DROPPED_OFF_DELICACY', 'CANCELLED'],
}

def is_deliver_next_state(old_state, new_state):
    '''
    Returns boolean if new_state is a next state for old_state
    '''
    try:
        state = deliver_states[old_state]
        if new_state in state:
            return True
        else:
            return False
    except KeyError:
        return False