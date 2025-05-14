params ["_type", "_value"];

switch (_type) do
{
	case 1: { my_unit = objectFromNetId _value };
	case 2: { my_unit = _value call BIS_fnc_getUnitByUID };
	default { my_unit = _value };
};

[my_unit, 0] spawn MOO_fnc_update_board;

my_unit addEventHandler ["HandleScore", {
	params ["_unit", "_object", "_score"];
	[_unit, _score] spawn MOO_fnc_update_board;
}];

