/*
 * This file is part of the IDA research data storage service
 *
 * Copyright (C) 2018 Ministry of Education and Culture, Finland
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License,
 * or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
 * License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 *
 * @author    CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
 * @license   GNU Affero General Public License, version 3
 * @link      https://research.csc.fi/
 */

(function () {

    var TEMPLATE =
        '<div id="idaTabView">' +

        '<div id="spinnerWrapper"><div id="spinner"></div></div>' +

        '<div id="rootProjectFolder" style="display: none">' +
        '<div class="idaWarning"><p>' +
        t('ida', 'Root project folders may not be modified.') +
        '</p><p>' +
        t('ida', 'See the <a href="https://www.fairdata.fi/en/ida/user-guide" target="_blank">IDA User&apos;s Guide</a> for details.') +
        '</p></div>' +
        '</div>' +

        '<div id="stagingFolder" style="display: none">' +
        '<table class="idaTable">' +
        '<tr><td align="center">' +
        '<input type="button" value="' + t('ida', 'Freeze') + '" id="freezeFolderButton"/>' +
        '</td></tr>' +
        '</table>' +
        '<div class="idaWarning"><p><b>' +
        t('ida', 'NOTICE') + '</b>: ' +
        t('ida', 'Be absolutely sure you want to freeze the folder before proceeding.') +
        '</p><p>' +
        t('ida', 'Freezing will move all files within the selected folder to the frozen area, making all files read-only and visible to other services, and will initiate several background operations.') +
        '</p><p>' +
        t('ida', 'Frozen files will be replicated to separate physical storage to guard against loss of data due to hardware failure.') +
        '</p><p>' +
        t('ida', 'The action cannot be terminated before it is complete. Depending on the amount of data, the background operations may take several hours.') +
        '</p><p>' +
        t('ida', 'Once initiated, the progress of the action can be checked from the <a href="../ida/actions/pending">Pending Actions</a> view.') +
        '</p><p>' +
        t('ida', 'See the <a href="https://www.fairdata.fi/en/ida/user-guide" target="_blank">IDA User&apos;s Guide</a> for details.') +
        '</p></div>' +
        '</div>' +

        '<div id="stagingFile" style="display: none">' +
        '<table class="idaTable">' +
        '<tr><td align="center">' +
        '<input type="button" value="' + t('ida', 'Freeze') + '" id="freezeFileButton"/>' +
        '</td></tr>' +
        '</table>' +
        '<div class="idaWarning"><p><b>' +
        t('ida', 'NOTICE') + '</b>: ' +
        t('ida', 'Be absolutely sure you want to freeze the file before proceeding.') +
        '</p><p>' +
        t('ida', 'Freezing will move the selected file to the frozen area, making it read-only and visible to other services, and will initiate several background operations.') +
        '</p><p>' +
        t('ida', 'The frozen file will be replicated to separate physical storage to guard against loss of data due to hardware failure.') +
        '</p><p>' +
        t('ida', 'The action cannot be terminated before it is complete. Depending on the size of the file, the background operations may take several hours.') +
        '</p><p>' +
        t('ida', 'Once initiated, the progress of the action can be checked from the <a href="../ida/actions/pending">Pending Actions</a> view.') +
        '</p><p>' +
        t('ida', 'See the <a href="https://www.fairdata.fi/en/ida/user-guide" target="_blank">IDA User&apos;s Guide</a> for details.') +
        '</p></div>' +
        '</div>' +

        '<div id="frozenFilePending" style="display: none">' +
        '<table class="idaTable">' +
        '<tr><th>' + t('ida', 'Action') + ':</th><td id="frozenFilePendingAction"></td></tr>' +
        '</table>' +
        '<p>' +
        t('ida', 'This file is part of an ongoing action.') +
        '</p><p>' +
        t('ida', 'Additional information will be available once the action is complete.') +
        '</p><p>' +
        t('ida', 'The progress of the ongoing action can be viewed by clicking on the action ID above.') +
        '</p><p>' +
        t('ida', 'See the <a href="https://www.fairdata.fi/en/ida/user-guide" target="_blank">IDA User&apos;s Guide</a> for details.') +
        '</p></div>' +
        '</div>' +

        '<div id="frozenFolder" style="display: none">' +
        '<table class="idaTable">' +
        '<tr><td>' +
        '<input type="button" value="' + t('ida', 'Unfreeze') + '" id="unfreezeFolderButton"/>' +
        '<input type="button" value="' + t('ida', 'Delete') + '" id="deleteFolderButton"/>' +
        '</td></tr>' +
        '</table>' +
        '<div class="idaWarning"><p><b>' +
        t('ida', 'NOTICE') + '</b>: ' +
        t('ida', 'Be absolutely sure you want to unfreeze or delete the folder, and all files within it, before proceeding with either option.') +
        '</p><p><b>' +
        t('ida', 'Unfrozen and deleted files will no longer to be accessible to other services, making all external references to them invalid. All replicated copies of unfrozen and deleted files will be removed.') +
        '</b></p><p>' +
        t('ida', 'Unfreezing will move all files within the specified folder back to the staging area, making them fully editable.') + ' ' +
        t('ida', 'Deleting will entirely remove the selected folder, and all files within it, from the service.') + ' ' +
        t('ida', 'Either action will initiate several background operations.') +
        '</p><p>' +
        t('ida', 'The action cannot be terminated before it is complete. Depending on the amount of data, the background operations may take several hours.') +
        '</p><p><b>' +
        t('ida', 'THIS ACTION CANNOT BE UNDONE.') +
        '</b></p><p>' +
        t('ida', 'Once initiated, the progress of the action can be checked from the <a href="../ida/actions/pending">Pending Actions</a> view.') +
        '</p><p>' +
        t('ida', 'See the <a href="https://www.fairdata.fi/en/ida/user-guide" target="_blank">IDA User&apos;s Guide</a> for details.') +
        '</p></div>' +
        '</div>' +

        '<div id="frozenFile" style="display: none">' +
        '<table class="idaTable">' +
        '<tr><th>' + t('ida', 'Action') + ':</th><td id="frozenFileAction"></td></tr>' +
        '<tr><th>' + t('ida', 'File ID') + ':</th><td id="frozenFileId"></td></tr>' +
        '<tr><th>' + t('ida', 'Frozen') + ':</th><td id="frozenFileFrozen"></td></tr>' +
        '<tr><th>' + t('ida', 'Size') + ':</th><td id="frozenFileSize"></td></tr>' +
        '<tr><th>' + t('ida', 'Checksum') + ':</th><td id="frozenFileChecksum"></td></tr>' +
        '<tr><td colspan="2" align="center">' +
        '<input type="button" value="' + t('ida', 'Unfreeze') + '" id="unfreezeFileButton"/>' +
        '<input type="button" value="' + t('ida', 'Delete') + '" id="deleteFileButton"/>' +
        '</td></tr>' +
        '</table>' +
        '<div class="idaWarning"><p><b>' +
        t('ida', 'NOTICE') + '</b>: ' +
        t('ida', 'Be absolutely sure you want to unfreeze or delete the file before proceeding with either option.') +
        '</p><p><b>' +
        t('ida', 'Unfrozen and deleted files will no longer to be accessible to other services, making all external references to them invalid. All replicated copies of unfrozen and deleted files will be removed.') +
        '</b></p><p>' +
        t('ida', 'Unfreezing will move the selected file back to the staging area, making it fully editable.') + ' ' +
        t('ida', 'Deleting will entirely remove the selected file from the service.') + ' ' +
        t('ida', 'Either action will initiate several background operations.') +
        '</p><p>' +
        t('ida', 'The action cannot be terminated before it is complete. Depending on the size of the file, the background operations may take several hours.') +
        '</p><p><b>' +
        t('ida', 'THIS ACTION CANNOT BE UNDONE.') +
        '</b></p><p>' +
        t('ida', 'Once initiated, the progress of the action can be checked from the <a href="../ida/actions/pending">Pending Actions</a> view.') +
        '</p><p>' +
        t('ida', 'See the <a href="https://www.fairdata.fi/en/ida/user-guide" target="_blank">IDA User&apos;s Guide</a> for details.') +
        '</p></div>' +
        '</table>' +
        '</div>' +

        '<div id="debug" style="display: none"></div>' +

        '</div>';

    function freezeFolder(e) {
        OC.dialogs.confirm(
            t('ida', 'Are you sure you want to freeze all files within this folder, moving them to the frozen area and making them read-only?') + ' ' +
            t('ida', 'The action cannot be terminated before it is complete. Depending on the amount of data, the background operations may take several hours.'),
            t('ida', 'Freeze Folder?'),
            function (result) {
                if (result) {
                    $(freezeFolderButton).prop('disabled', true);
                    executeAction(e.data.param, 'freeze');
                }
            },
            true
        );
    }

    function freezeFile(e) {
        OC.dialogs.confirm(
            t('ida', 'Are you sure you want to freeze this file, moving it to the frozen area and making it read-only?') + ' ' +
            t('ida', 'The action cannot be terminated before it is complete. Depending on the size of the file, the background operations may take several hours.'),
            t('ida', 'Freeze File?'),
            function (result) {
                if (result) {
                    $(freezeFileButton).prop('disabled', true);
                    executeAction(e.data.param, 'freeze');
                }
            },
            true
        );
    }

    function unfreezeFolder(e) {
        OC.dialogs.confirm(
            t('ida', 'Are you sure you want to unfreeze all files within this folder, and move them back to the staging area?') + ' ' +
            t('ida', 'The action cannot be terminated before it is complete. Depending on the amount of data, the background operations may take several hours.') + ' ' +
            t('ida', 'THIS ACTION CANNOT BE UNDONE.'),
            t('ida', 'Unfreeze Folder?'),
            function (result) {
                if (result) {
                    $(unfreezeFolderButton).prop('disabled', true);
                    $(deleteFolderButton).prop('disabled', true);
                    executeAction(e.data.param, 'unfreeze');
                }
            },
            true
        );
    }

    function unfreezeFile(e) {
        OC.dialogs.confirm(
            t('ida', 'Are you sure you want to unfreeze this file, and move it back to the staging area?') + ' ' +
            t('ida', 'The action cannot be terminated before it is complete. Depending on the size of the file, the background operations may take several hours.') + ' ' +
            t('ida', 'THIS ACTION CANNOT BE UNDONE.'),
            t('ida', 'Unfreeze File?'),
            function (result) {
                if (result) {
                    $(unfreezeFileButton).prop('disabled', true);
                    $(deleteFileButton).prop('disabled', true);
                    executeAction(e.data.param, 'unfreeze');
                }
            },
            true
        );
    }

    function deleteFolder(e) {
        OC.dialogs.confirm(
            t('ida', 'Are you sure you want to delete this folder, permanently removing it and all files within it from the service?') + ' ' +
            t('ida', 'The action cannot be terminated before it is complete. Depending on the amount of data, the background operations may take several hours.') + ' ' +
            t('ida', 'THIS ACTION CANNOT BE UNDONE.'),
            t('ida', 'Delete Folder?'),
            function (result) {
                if (result) {
                    $(deleteFolderButton).prop('disabled', true);
                    executeAction(e.data.param, 'delete');
                }
            },
            true
        );
    }

    function deleteFile(e) {
        OC.dialogs.confirm(
            t('ida', 'Are you sure you want to delete this file, permanently removing it from the service?') + ' ' +
            t('ida', 'The action cannot be terminated before it is complete.') + ' ' +
            t('ida', 'Depending on the size of the file, the background operations may take several hours.') + ' ' +
            t('ida', 'THIS ACTION CANNOT BE UNDONE.'),
            t('ida', 'Delete File?'),
            function (result) {
                if (result) {
                    $(deleteFileButton).prop('disabled', true);
                    executeAction(e.data.param, 'delete');
                }
            },
            true
        );
    }

    function executeAction(fileInfo, action) {
        $(spinner).show();
        var fullpath = fileInfo.getFullPath();
        var project = OCA.IDA.Util.extractProjectName(fullpath);
        var pathname = OCA.IDA.Util.stripRootFolder(fullpath);
        var nodeId = fileInfo.get('id');
        var params = { nextcloudNodeId: nodeId, project: project, pathname: pathname };
        $.ajax({
            cache: false,
            url: OC.generateUrl('/apps/ida/api/' + action),
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(params),
            success: function (data) {
                $(spinner).hide();
                if (data['action'] === 'freeze') {
                    OC.dialogs.confirmHtml(
                        t('ida', 'The data has been successfully frozen and moved to the frozen project space.') + ' ' +
                        t('ida', 'Depending on the amount of data, the background operations may still take several hours.') + ' ' +
                        t('ida', 'The initiated action is') + ' <a style="color: #007FAD;" href="/apps/ida/action/' + data['pid'] + '">' + data['pid'] + '</a>. ' +
                        t('ida', 'Do you wish to view the data in its frozen location?'),
                        t('ida', 'Action initiated successfully. Show frozen data?'),
                        function (result) {
                            if (result) {
                                var url = '/apps/files/?dir=' + encodeURIComponent('/' + data['project'] + OCA.IDA.Util.getParentPathname(data['pathname']));
                                $(spinner).show();
                                window.location.assign(url);
                            }
                            else {
                                $(spinner).show();
                                window.location.reload(true);
                            }
                        },
                        true
                    );
                }
                else if (data['action'] === 'unfreeze') {
                    OC.dialogs.confirmHtml(
                        t('ida', 'The data has been successfully unfrozen and moved back to the project staging space.') + ' ' +
                        t('ida', 'Depending on the amount of data, the background operations may still take several hours.') + ' ' +
                        t('ida', 'The initiated action is') + ' <a style="color: #007FAD;" href="/apps/ida/action/' + data['pid'] + '">' + data['pid'] + '</a>. ' +
                        t('ida', 'Do you wish to view the data in its staging location?'),
                        t('ida', 'Action initiated successfully. Show unfrozen data?'),
                        function (result) {
                            if (result) {
                                var url = '/apps/files/?dir=' + encodeURIComponent('/' + data['project'] + OCA.IDAConstants.STAGING_FOLDER_SUFFIX + OCA.IDA.Util.getParentPathname(data['pathname']));
                                $(spinner).show();
                                window.location.assign(url);
                            }
                            else {
                                $(spinner).show();
                                window.location.reload(true);
                            }
                        },
                        true
                    );
                }
                else { // action === 'delete')
                    OC.dialogs.message(
                        t('ida', 'The files have been successfully deleted.') + ' ' +
                        t('ida', 'Depending on the amount of data, the background operations may still take several hours.') + ' ' +
                        t('ida', 'The initiated action is') + ' <a style="color: #007FAD;" href="/apps/ida/action/' + data['pid'] + '">' + data['pid'] + '</a>.',
                        t('ida', 'Action initiated successfully. Files deleted.'),
                        'info',
                        OCdialogs.OK_BUTTON,
                        function (result) {
                            $(spinner).show();
                            window.location.reload(true);
                        },
                        true,
                        true
                    );
                }
                return true;
            },
            error: function (data) {
                $(spinner).hide();
                if (action === 'freeze') {
                    OC.dialogs.alert(
                        t('ida', 'Unable to freeze the specified files:' + ' ' + data.responseJSON.message),
                        t('ida', 'Action Failed'),
                        function (result) {
                            window.location.reload(true);
                        },
                        true
                    );
                }
                else if (action === 'unfreeze') {
                    OC.dialogs.alert(
                        t('ida', 'Unable to unfreeze the specified files:' + ' ' + data.responseJSON.message),
                        t('ida', 'Action Failed'),
                        function (result) {
                            window.location.reload(true);
                        },
                        true
                    );
                }
                else { // action === 'delete')
                    OC.dialogs.alert(
                        t('ida', 'Unable to delete the specified files:' + ' ' + data.responseJSON.message),
                        t('ida', 'Action Failed'),
                        function (result) {
                            window.location.reload(true);
                        },
                        true
                    );
                }
                return false;
            }
        });
    }

    /**
     * @class OCA.IDA.IDATabView
     * @memberof OCA.IDA
     * @classdesc
     *
     * Shows publication information for file
     *
     */
    var IDATabView = OCA.Files.DetailTabView.extend(
        /** @lends OCA.IDA.IDATabView.prototype */{
            id: 'idaTabView',
            className: 'idaTabView tab',

            _label: 'ida',

            events: {},

            getLabel: function () {
                return t('ida', 'Freezing');
            },

            nextPage: function () {
            },

            _onClickShowMoreVersions: function (ev) {
            },

            _onClickRevertVersion: function (ev) {
            },

            _toggleLoading: function (state) {
            },

            _onRequest: function () {
            },

            _onEndRequest: function () {
            },

            _onAddModel: function (model) {
            },

            itemTemplate: function (data) {
            },

            setFileInfo: function (fileInfo) {
                if (fileInfo) {
                    this.fileInfo = fileInfo;
                    this.render();
                }
            },

            _formatItem: function (version) {
            },

            /**
             * Renders the node details tab view
             */
            render: function () {

                //this.$el.html(this.template());
                this.$el.html(TEMPLATE);

                var fileInfo = this.fileInfo;
                var fullPath = fileInfo.getFullPath();
                var isRootProjectFolder = OCA.IDA.Util.testIfRootProjectFolder(fullPath);

                $(spinner).hide();

                $(freezeFolderButton).bind('click', {param: fileInfo}, freezeFolder);
                $(freezeFileButton).bind('click', {param: fileInfo}, freezeFile);
                $(unfreezeFolderButton).bind('click', {param: fileInfo}, unfreezeFolder);
                $(unfreezeFileButton).bind('click', {param: fileInfo}, unfreezeFile);
                $(deleteFolderButton).bind('click', {param: fileInfo}, deleteFolder);
                $(deleteFileButton).bind('click', {param: fileInfo}, deleteFile);

                if (isRootProjectFolder) {
                    $(rootProjectFolder).show();
                }
                else {

                    var project = OCA.IDA.Util.extractProjectName(fullPath);
                    var pathname = OCA.IDA.Util.stripRootFolder(fullPath);
                    var isFolder = this.fileInfo.isDirectory();
                    var isFrozen = OCA.IDA.Util.testIfFrozen(fullPath);

                    if (isFrozen) {

                        if (isFolder) {
                            $(frozenFolder).show();
                        }

                        else {

                            // Fetch frozen file details...

                            $.ajax({

                                cache: false,
                                url: OC.generateUrl('/apps/ida/api/files/byNextcloudNodeId/' + this.fileInfo.id),
                                type: 'GET',
                                contentType: 'application/json',

                                success: function (fileInfo) {

                                    var filePid = fileInfo['pid'];
                                    var actionPid = fileInfo['action'];
                                    var fileFrozen = OCA.IDA.Util.localizeTimestamp(fileInfo['frozen']);
                                    var fileSize = fileInfo['size'];
                                    var fileChecksum = fileInfo['checksum'];

                                    // Fetch action details...

                                    $.ajax({

                                        cache: false,
                                        url: OC.generateUrl('/apps/ida/api/actions/' + actionPid),
                                        type: 'GET',
                                        contentType: 'application/json',

                                        success: function (actionInfo) {

                                            var isPending = actionInfo ? !(actionInfo['completed'] || actionInfo['failed'] || actionInfo['cleared']) : false;

                                            if (isPending) {
                                                $(frozenFilePendingAction).html('<a href="/apps/ida/action/' + actionPid + '">' + actionPid + '</a>');
                                                $(frozenFilePending).show();
                                            }
                                            else {
                                                $(frozenFileAction).html('<a href="/apps/ida/action/' + actionPid + '">' + actionPid + '</a>');
                                                $(frozenFileId).html(filePid);
                                                $(frozenFileFrozen).html(fileFrozen);
                                                $(frozenFileSize).html(fileSize);
                                                $(frozenFileChecksum).html(fileChecksum);
                                                $(frozenFile).show();
                                            }
                                        },

                                        error: function (x) {
                                            // This shouldn't ever happen, but we'll fail gracefully...
                                            $(frozenFile).show();
                                        }
                                    });
                                },

                                error: function (x) {
                                    // This shouldn't ever happen, but we'll fail gracefully...
                                    $(frozenFile).show();
                                }
                            });
                        }
                    }
                    else {
                        if (isFolder) {
                            $(stagingFolder).show();
                        }
                        else {
                            $(stagingFile).show();
                        }
                    }
                }

                this.delegateEvents();
            }

        });

    OCA.IDA = OCA.IDA || {};

    OCA.IDA.IDATabView = IDATabView;

})();


