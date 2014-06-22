// Ortinating numbers: http://stackoverflow.com/questions/15809950/javascript-ordinal-suffix-for-numbers-with-specific-css-class
ordinate = function(num){
    var /*num = this,*/
        numStr = num.toString(),
        last = numStr.slice(-1),
        ord = '';
    switch (last) {
        case '1':
            ord = numStr.slice(-2) === '11' ? 'th' : 'st';
            break;
        case '2':
            ord = numStr.slice(-2) === '12' ? 'th' : 'nd';
            break;
        case '3':
            ord = numStr.slice(-2) === '13' ? 'th' : 'rd';
            break;
        default:
            ord = 'th';
            break;
    }
    return num.toString() + ord;
};

// Simple f'n for searching an array for another array
function containsLocation(array, location){
    for(var i = 0; i < array.length; i++){
        if (isEqual(array[i], location)){
            return true;
        }
    }
    return false;
}

// Equal function...I don't know.
function isEqual(one, two){
    if(one.length !== two.length){
        return false;
    }
    for(var i = 0; i < one.length; i++){
        if(one[i] !== two[i]){
            return false;
        }
    }
    return true;
}

// Provie an offset location for a marker to prevent stacking
function offset(location){
    var offset = 0.01;
    var newLocation = new Array();
    for(var i = 0; i < location.length; i++){
        newLocation[i] = location[i] + ((offset*Math.random())-(offset/2));
    }
    return newLocation;
}