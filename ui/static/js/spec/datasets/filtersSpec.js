describe('displaySize filter', function () {
    beforeEach(module('pype.datasets'));

    var $filter;

    beforeEach(inject(function (_$filter_) {
        $filter = _$filter_;
    }));

    it('returns N/A when input is null', function () {
        var displaySize = $filter('displaySize');
        expect(displaySize(null)).toEqual('N/A');
    });

    it('returns N/A when input is null', function () {
        var displaySize = $filter('displaySize');
        expect(displaySize(undefined)).toEqual('N/A');
    });

    it('returns a readable value', function () {
        var displaySize = $filter('displaySize');
        expect(displaySize(356)).toEqual('356 B');
        expect(displaySize(1024)).toEqual('1.00 KB');
        expect(displaySize(1536)).toEqual('1.50 KB');
        expect(displaySize(1024 * 1024)).toEqual('1.00 MB');
        expect(displaySize(1024 * 1024 * 1024)).toEqual('1.00 GB');
        expect(displaySize(1024 * 1024 * 1024 * 1024)).toEqual('1.00 TB');

        expect(displaySize(1024 + 450)).toEqual('1.44 KB');
        expect(displaySize(12 * 1024 + 450)).toEqual('12.4 KB');
        expect(displaySize(112 * 1024 + 450)).toEqual('112 KB');
    });

});


describe('displayDate filter', function () {
    beforeEach(module('pype.datasets'));

    var $filter;

    beforeEach(inject(function (_$filter_) {
        $filter = _$filter_;
    }));

    it('returns a readable date', function () {
        var displayDate = $filter('displayDate');
        expect(displayDate(new Date(2016, 0, 25, 14, 49, 0))).toEqual('Mon, Jan 25, 2016 2:49 PM');
    });

});


describe('folderIsSubfolderOf filter', function () {
    beforeEach(module('pype.datasets'));
    var $filter;
    beforeEach(inject(function (_$filter_) {
        $filter = _$filter_;
    }));

    it('returns only children of the given folder', function () {
        var folderIsSubfolderOf = $filter('folderIsSubfolderOf');

        var parent = {pk: 10, parent: null};
        var folders = [
            {pk: 10, parent: null},
            {pk: 11, parent: 10},
            {pk: 12, parent: 11}
        ];

        expect(folderIsSubfolderOf(folders, parent)).toEqual([folders[1]]);

    });
});


describe('isRootFolder filter', function () {
    beforeEach(module('pype.datasets'));
    var $filter;
    beforeEach(inject(function (_$filter_) {
        $filter = _$filter_;
    }));

    it('returns only root folders', function () {
        var isRootFolder = $filter('isRootFolder');

        var parent = {pk: 10, parent: null};
        var folders = [
            {pk: 10, parent: null},
            {pk: 11, parent: 10},
            {pk: 12, parent: 11}
        ];

        expect(isRootFolder(folders)).toEqual([folders[0]]);
    });

});


describe('fileIsInFolder filter', function () {
    beforeEach(module('pype.datasets'));
    var $filter;
    beforeEach(inject(function (_$filter_) {
        $filter = _$filter_;
    }));

    it('returns only file that are in the folder', function () {
        var fileIsInFolder = $filter('fileIsInFolder');

        var folders = [
            {pk: 10, parent: null},
            {pk: 11, parent: 10},
            {pk: 12, parent: 11}
        ];

        var files = [
            {pk: 10, folder: 11},
            {pk: 11, folder: 12},
            {pk: 12, folder: 10}
        ];

        expect(fileIsInFolder(files, folders[0])).toEqual([files[2]]);

    });
});
