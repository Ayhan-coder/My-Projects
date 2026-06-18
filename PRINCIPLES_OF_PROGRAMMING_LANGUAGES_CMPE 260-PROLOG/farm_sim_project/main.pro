% Ali Ayhan Gunder
% 2021400219
% compiling: yes
% complete: yes


:- ['cmpefarm.pro'].
:- init_from_map.


% 1- agents_distance(+Agent1, +Agent2, -Distance)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Calculate Manhattan distance between two agents
agents_distance(Agent1, Agent2, Distance) :-
    % Get coordinates of first agent
    get_dict(x, Agent1, X1),
    get_dict(y, Agent1, Y1),
    % Get coordinates of second agent
    get_dict(x, Agent2, X2),
    get_dict(y, Agent2, Y2),
    % Calculate absolute differences
    DX is abs(X1 - X2),
    DY is abs(Y1 - Y2),
    % Manhattan distance = |x1-x2| + |y1-y2|
    Distance is DX + DY.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% 2- number_of_agents(+State, -NumberOfAgents)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Count how many agents are in the game
number_of_agents([Agents, _], NumberOfAgents) :-
    % Get all agent pairs from the dictionary
    dict_pairs(Agents, _, Pairs),
    % Count the number of pairs
    length(Pairs, NumberOfAgents).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% 3- value_of_farm(+State, -Value)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Calculate total value of all agents and objects on the farm
value_of_farm([Agents, Objects], TotalValue) :-
    % Get agent-value pairs from dictionary
    dict_pairs(Agents, _, AgentPairs),
    % Get object-value pairs from dictionary  
    dict_pairs(Objects, _, ObjectPairs),
    % Find all agent values
    findall(VA, (
        member(_-Agent, AgentPairs),           % For each agent
        get_dict(subtype, Agent, Subtype),     % Get its type
        value(Subtype, VA)                     % Get its value
    ), AgentValues),
    % Find all object values
    findall(VO, (
        member(_-Object, ObjectPairs),         % For each object
        get_dict(subtype, Object, Subtype),    % Get its type
        value(Subtype, VO)                     % Get its value
    ), ObjectValues),
    % Combine both lists
    concat_lists(AgentValues, ObjectValues, AllValues),
    % Calculate the total sum
    calculate_total(AllValues, TotalValue).

% Helper: Add all numbers in a list
calculate_total([], 0).
calculate_total([H|T], Sum) :-
    calculate_total(T, RestSum),
    Sum is H + RestSum.

% Helper: Join two lists together
concat_lists([], L, L).
concat_lists([H|T], L, [H|Result]) :-
    concat_lists(T, L, Result).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% 4- find_food_coordinates(+State, +AgentId, -Coordinates)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find all food that this agent can eat
find_food_coordinates([Agents, Objects], AgentId, Coordinates) :-
    % Get the agent from dictionary
    get_dict(AgentId, Agents, Agent),
    % Get what type of agent this is
    get_dict(subtype, Agent, Subtype),
    % Get all objects as key-value pairs
    dict_pairs(Objects, _, ObjectPairs),
    % Find all food coordinates this agent can eat
    findall([X, Y], (
        member(_-Object, ObjectPairs),         % For each object
        get_dict(type, Object, food),          % Check if it's food
        get_dict(subtype, Object, FoodType),   % Get food type
        can_eat(Subtype, FoodType),            % Check if agent can eat it
        get_dict(x, Object, X),                % Get X coordinate
        get_dict(y, Object, Y)                 % Get Y coordinate
    ), Coordinates),
    Coordinates \= [].  % Make sure we found some food
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



% 5- find_nearest_agent(+State, +AgentId, -Coordinates, -NearestAgent)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find the closest agent to a given agent
find_nearest_agent([Agents, _], AgentId, Coordinates, NearestAgent) :-
    % Get the main agent we want to compare
    get_dict(AgentId, Agents, Agent),
    % Get all agents as pairs
    dict_pairs(Agents, _, AgentPairs),
    % Remove the main agent from the list (can't be nearest to itself)
    exclude(is_same_id(AgentId), AgentPairs, OtherAgents),
    % Calculate distance to each other agent
    findall([D, A], (
        member(_-A, OtherAgents),              % For each other agent
        agents_distance(Agent, A, D)           % Calculate distance
    ), DistAgentPairs),
    % Sort by distance, get the closest one
    sort(DistAgentPairs, [[_, NearestAgent]|_]),
    % Get coordinates of the nearest agent
    get_dict(x, NearestAgent, X),
    get_dict(y, NearestAgent, Y),
    Coordinates = [X, Y].

% Helper: Check if this agent is the same as the one we're looking for
is_same_id(Id, Key-_) :- Id =:= Key.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% 6- find_nearest_food(+State, +AgentId, -Coordinates, -FoodType, -Distance)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find the closest food that this agent can eat
find_nearest_food([Agents, Objects], AgentId, Coordinates, FoodType, Distance) :-
    % Get the agent and its position
    get_dict(AgentId, Agents, Agent),
    get_dict(subtype, Agent, Subtype),
    get_dict(x, Agent, X1),
    get_dict(y, Agent, Y1),
    % Get all objects as pairs
    dict_pairs(Objects, _, ObjectPairs),
    % Find all food this agent can eat with distances
    findall([D, [X, Y], FType], (
        member(_-Object, ObjectPairs),         % For each object
        get_dict(type, Object, food),          % Check if it's food
        get_dict(subtype, Object, FType),      % Get food type
        can_eat(Subtype, FType),               % Check if agent can eat it
        get_dict(x, Object, X),                % Get food X coordinate
        get_dict(y, Object, Y),                % Get food Y coordinate
        D is abs(X1 - X) + abs(Y1 - Y)        % Calculate Manhattan distance
    ), FoodList),
    FoodList \= [],  % Make sure we found some food
    % Sort by distance and get the closest one
    sort(FoodList, [[Distance, Coordinates, FoodType] | _]).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




% 7- move_to_coordinate(+State, +AgentId, +X, +Y, -ActionList, +DepthLimit)    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find a path for the agent to reach target coordinates
move_to_coordinate(State, AgentId, X, Y, ActionList, DepthLimit) :-
    % Use depth-first search to find the path
    dfs(State, AgentId, X, Y, [], ActionList, DepthLimit).

% Base case: agent is already at the goal position
dfs(State, AgentId, X, Y, Path, ActionList, _) :-
    get_agent(State, AgentId, Agent),
    get_dict(x, Agent, AgentX),
    get_dict(y, Agent, AgentY),
    AgentX =:= X,                              % Check if X matches
    AgentY =:= Y,                              % Check if Y matches
    reverse(Path, ActionList).                 % Return the path taken

% Recursive case: try different actions to reach the goal
dfs(State, AgentId, X, Y, Path, ActionList, DepthLimit) :-
    DepthLimit > 0,                            % Make sure we have moves left
    get_agent(State, AgentId, Agent),
    get_dict(subtype, Agent, Subtype),
    can_move(Subtype, Action),                 % Check what moves are allowed
    make_one_action(Action, State, AgentId, NewState), % Try the action
    \+ member(Action, Path),                   % Don't repeat same action
    NewDepth is DepthLimit - 1,                % Reduce remaining depth
    dfs(NewState, AgentId, X, Y, [Action | Path], ActionList, NewDepth).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% 8- move_to_nearest_food(+State, +AgentId, -ActionList, +DepthLimit)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Move agent to the closest food it can eat
move_to_nearest_food(State, AgentId, ActionList, DepthLimit) :-
    % First, find the nearest food
    find_nearest_food(State, AgentId, [X, Y], _, _),
    % Then, move to that food's coordinates
    move_to_coordinate(State, AgentId, X, Y, ActionList, DepthLimit).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



% 9- consume_all(+State, +AgentId, -NumberOfMoves, -Value, NumberOfChildren +DepthLimit)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Agent eats all food it can reach within the depth limit
consume_all(State, AgentId, NumberOfMovements, Value, NumberOfChildren, DepthLimit) :-
    % Start the eating loop
    consume_loop(State, AgentId, 0, DepthLimit, 0, FinalState, NumberOfMovements),
    % Calculate final farm value
    value_of_farm(FinalState, Value),
    % Get the agent's final number of children
    get_agent(FinalState, AgentId, Agent),
    get_dict(children, Agent, NumberOfChildren).

% Recursive loop: move → eat → repeat
consume_loop(State, AgentId, Used, Limit, MovesAcc, FinalState, TotalMoves) :-
    Remain is Limit - Used,                   % Calculate remaining moves
    Remain > 0,                               % Make sure we have moves left
    % Check if there's food available and we can reach it
    find_nearest_food(State, AgentId, [X, Y], _, _),
    move_to_coordinate(State, AgentId, X, Y, ActionList, Remain),
    length(ActionList, L),                    % Count moves needed
    make_series_of_actions(ActionList, State, AgentId, MidState),
    make_one_action(eat, MidState, AgentId, NewState), % Eat the food
    NewUsed is Used + L + 1,                  % Add 1 for the eat action
    NewAcc is MovesAcc + L + 1,               % Update total moves
    consume_loop(NewState, AgentId, NewUsed, Limit, NewAcc, FinalState, TotalMoves).

% Base case: no food reachable or depth limit reached
consume_loop(State, _, _, _, MovesAcc, State, MovesAcc) :-
    !.  % Cut to prevent backtracking
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

