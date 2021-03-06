sell_states = {
    'DEFAULT': ['1'],
    'CANCELLED': ['DEFAULT'],

    'REQUEST_CODE': ['REQUEST_CODE', 'CANCELLED'],
    'VENDOR_LOCATION': ['VENDOR_LOCATION', 'CANCELLED'],

    'JOLLOF_PENDING_DELIVERIES': ['JOLLOF_PENDING_DELIVERIES'],
    'JOLLOF_PENDING_RESERVATIONS': ['JOLLOF_PENDING_RESERVATIONS'],
    'JOLLOF_ACCEPTED_DELIVERIES': ['JOLLOF_ACCEPTED_DELIVERIES'],
    'JOLLOF_ACCEPTED_RESERVATIONS': ['JOLLOF_ACCEPTED_RESERVATIONS'],

    'DELICACY_PENDING_DELIVERIES': ['DELICACY_PENDING_DELIVERIES'],
    'DELICACY_PENDING_RESERVATIONS': ['DELICACY_PENDING_RESERVATIONS'],
    'DELICACY_ACCEPTED_DELIVERIES': ['DELICACY_ACCEPTED_DELIVERIES'],
    'DELICACY_ACCEPTED_RESERVATIONS': ['DELICACY_ACCEPTED_RESERVATIONS'],
    
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