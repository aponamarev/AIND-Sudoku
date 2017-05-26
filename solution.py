assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

def diagonal(A,B):
    assert len(A)==len(B), "Error: lists of wrong size provided. A - {}, B - {}".format(len(A),len(B))
    return [A[i]+B[i] for i in range(len(A))]


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
boxes = cross(rows, cols)
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
diagonals = [diagonal(rows, cols), diagonal(rows[::-1], cols)]


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Identify twins in both rows and columns
    for search_space in (column_units, row_units):
        for subspace in search_space:
            # Check every box of subspace for twins
            for box in subspace:
                twins = []
                # Twins defined as a peer box that has the same value and the length of 2
                if len(values[box])==2:
                    for peer in subspace:
                        if (peer!=box) & (values[box]==values[peer]):
                            twins = [peer, box]
                # Eliminate the naked twins as possibilities for their peers
                if len(twins)>0:
                    # To minimize compute time, we should only run the algorithm on one of the twins
                    # (as they have the same value)
                    twin = twins[0]
                    subspace_extended = subspace
                    # if both twins are in the same box, eliminate twin values from box peers as well.
                    for square in square_units:
                        if (twins[0] in square) & (twins[1] in square):
                            subspace_extended = set(subspace_extended+square)

                    for digit in values[twin]:
                        # eliminate digits in twin values from the other peers
                        for peer in subspace_extended:
                            # ensure that twin values themselves are remain intact
                            if (peer not in twins) & (len(values[peer])>1):
                                assign_value(values, peer, values[peer].replace(digit,''))
    return values


def diagonal_sudoku(values):
    """Eliminate values using the diagonal strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Eliminate value of a solved box and check only choice condition for diagonal peers
    stalled = False
    # Repeat the cycle until no additional improvement is achieved
    while not stalled:
        # Check the number of solved values before applying the algorithm
        solved_values_before = len([box for box, value in values.items() if len(value) == 1])
        # Run the algorithm on both diagonals
        for search_space in diagonals:
            # Isolate the diagonal
            diagonal = dict((i, values[i]) for i in search_space)
            # eliminate
            solved_values = [box for box, value in diagonal.items() if len(value) == 1]
            for box in solved_values:
                digit = diagonal[box]
                for peer in diagonal.keys():
                    if peer!=box:
                        diagonal[peer] = diagonal[peer].replace(digit, '')
            # only choice
            for digit in '123456789':
                dplaces = [box for box, value in diagonal.items() if digit in value]
                if len(dplaces) == 1:
                    diagonal[dplaces[0]] = digit
            # update values
            for box, value in diagonal.items():
                values[box] = value
        # Check the number of solved values after the algorithm was applied
        solved_values_after = len([box for box, value in values.items() if len(value) == 1])
        # Verify if the solution was improved
        stalled = solved_values_before == solved_values_after

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    all_values = '123456789'
    grid = [(all_values if v=='.' else v) for v in grid]
    assert len(grid)==81, "grid variable has incorrect size: {}".format(len(grid))
    return dict(zip(boxes, grid))

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box, value in values.items() if len(value) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box, value in values.items() if len(value) == 1])
        values = eliminate(values)
        values = diagonal_sudoku(values)
        values = naked_twins(values)
        values = only_choice(values)
        solved_values_after = len([box for box, value in values.items() if len(value) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(value)==1 for value in values.values()):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(value), b) for b, value in values.items() if len(value)>1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    grid = grid_values(grid)
    return search(grid)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
