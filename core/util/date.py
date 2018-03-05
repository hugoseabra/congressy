"""
    Helper function used in an assortment of places.
"""

def create_years_list():
    years = []
    epoch = 1950
    for i in range(60):
        epoch += 1
        years.append(epoch)

    return years


