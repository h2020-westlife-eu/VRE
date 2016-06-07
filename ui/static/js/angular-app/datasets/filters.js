angular.module('pype.datasets')
    .filter('isRootFolder', isRootFolder)
    .filter('fileIsInFolder', fileIsInFolder)
    .filter('folderIsSubfolderOf', folderIsSubfolderOf)
    .filter('displaySize', displaySize)
    .filter('displayDate', displayDate);


function isRootFolder() {
    "use strict";
    return function (input) {
        var filtered = [];
        angular.forEach(input, function (item) {
            if (item.parent === null) {
                filtered.push(item);
            }
        });

        return filtered;
    };
}


function fileIsInFolder() {
    "use strict";
    return function (input, folder) {
        var filtered = [];
        var folder_pk;
        if (angular.isDefined(folder)) {
            folder_pk = folder.pk;
        }
        angular.forEach(input, function (item) {
            if (item.folder === folder_pk) {
                filtered.push(item);
            }
        });

        return filtered;
    };
}


function folderIsSubfolderOf() {
    "use strict";
    return function (input, folder) {
        var filtered = [];
        angular.forEach(input, function (item) {
            if (item.parent === folder.pk) {
                filtered.push(item);
            }
        });

        return filtered;
    };
}


function displaySize() {
    "use strict";

    function smartTruncate(number) {
        if (number < 10) {
            return number.toFixed(2);
        } else if (number < 100) {
            return number.toFixed(1);
        } else {
            return number.toFixed(0);
        }
    }

    return function (input) {
        if (input === null || input === undefined) {
            return 'N/A';
        }

        var prefixes = ['', 'K', 'M', 'G', 'T'];

        var idx = 0;
        var mul = 1;

        while (idx < (prefixes.length - 1)) {
            if (input < mul * 1024) {
                if (idx === 0) {
                    return (input / mul) + ' B';
                } else {
                    return smartTruncate(input / mul) + ' ' + prefixes[idx] + 'B';
                }
            } else {
                mul *= 1024;
                idx += 1;
            }
        }

        return smartTruncate(input / mul) + ' ' + prefixes[idx] + 'B';
    };
}


function displayDate() {
    "use strict";
    return function (input) {
        return moment(input).format('llll');
    };
}
