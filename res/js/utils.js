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