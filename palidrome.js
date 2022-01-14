let a = "Dog"
console.log(palidrome(a))

function palidrome(a) {

    let arr = a.split()
    let arr2 = []

    for(var i = arr.length-1; i > 0; i--) {
        arr2.push(arr[i])
    }
    if (arr2 === arr) {
        return true;
    } else {
        return false;
    }
}