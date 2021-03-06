<?php
/**
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
 * PHP Version 7
 *
 * @category  Owncloud
 * @package   IDA
 * @author    CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
 * @license   GNU Affero General Public License, version 3
 * @link      https://research.csc.fi/
 */

namespace OCA\IDA\Util;

use Exception;
use OC;
use OCP\Util;
use OC\User\User;

/**
 * Various access management functions
 */
class Access
{
    /**
     * Return a string of comma separated names of all projects to which the user belongs.
     *
     * @return string
     */
    public static function getUserProjects() {
        
        $userProjects = null;
        
        $user = \OC::$server->getUserSession()->getUser();
        $userId = $user->getUID();
        
        if (strlen($userId) <= 0) {
            throw new Exception('No user found for session.');
        }
        
        // Fetch names of all project groups to which the user belongs
        $projects = implode(',', \OC::$server->getGroupManager()->getUserGroupIds($user));
        
        Util::writeLog('ida', 'getUserProjects: projects=' . $projects, \OCP\Util::DEBUG);
        
        return $projects;
    }
    
    /**
     * Produced a clean, comma separated sequence of project names, with no superfluous whitespace.
     *
     * @param string $projects a comma separated sequence of project names
     *
     * @return string
     */
    public static function cleanProjectList($projects) {
        
        $cleanProjects = null;
        
        if ($projects != null) {
            $projects = trim($projects);
            $first = true;
            if ($projects != null && $projects != '') {
                foreach (explode(',', $projects) as $project) {
                    if ($first) {
                        $cleanProjects = trim($project);
                        $first = false;
                    }
                    else {
                        $cleanProjects = $cleanProjects . ',' . trim($project);
                    }
                }
            }
        }
        
        return $cleanProjects;
    }
    
    /**
     * Throw exception if current user does not have rights to access the specified project (either is not a member
     * of the project or is not an admin).
     *
     * @param string $project the project name
     *
     * @throws Exception
     */
    public static function verifyIsAllowedProject($project) {
        
        $userId = \OC::$server->getUserSession()->getUser()->getUID();
        
        Util::writeLog('ida', 'verifyIsAllowedProject: userId=' . $userId . ' project=' . $project, \OCP\Util::DEBUG);
        
        if (strlen($userId) <= 0) {
            throw new Exception('No user found for session.');
        }
        
        // If user is PSO user for project, return (OK)
        if ($userId == strtolower(Constants::PROJECT_USER_PREFIX . $project)) {
            return;
        }
        
        // Throw exception if user is admin or does not belong to specified project group
        
        if ($userId === 'admin' || !\OC::$server->getGroupManager()->isInGroup($userId, $project)) {
            throw new Exception('Session user does not belong to the specified project.');
        }
    }
    
    /**
     * Returns true if the project lock file exists (e.g. due to an ongoing action), else returns false.
     *
     * @param string $project          the project name
     * @param string $lockFilePathname the full system pathname of the project lock file, if known
     *
     * @return bool
     */
    public static function projectIsLocked($project, $lockFilePathname = null) {
        if (!$project) {
            throw new Exception('Null project');
        }
        Util::writeLog('ida', 'projectIsLocked: project=' . $project . ' lockFilePathname=' . $lockFilePathname, \OCP\Util::DEBUG);
        if ($lockFilePathname == null) {
            $lockFilePathname = self::buildLockFilePathname($project);
        }
        
        return (file_exists($lockFilePathname));
    }
    
    /**
     * Locks the specified project by creating the project lock file.
     *
     * Returns true on success, else returns false. Always fails if the project is already locked or if the service is locked.
     *
     * @param string $project the project name
     *
     * @return bool
     */
    public static function lockProject($project) {
        if (!$project) {
            throw new Exception('Null project');
        }
        Util::writeLog('ida', 'lockProject: project=' . $project, \OCP\Util::DEBUG);
        // If service is locked, no project may be locked, and service remains locked
        if (self::projectIsLocked('all')) {
            if ($project !== 'all') {
                return false;
            }
            return true;
        }
        $lockFilePathname = self::buildLockFilePathname($project);
        if (self::projectIsLocked($project, $lockFilePathname)) {
            return false;
        }
        if (!touch($lockFilePathname)) {
            throw new Exception('Failed to create lock file for project ' . $project);
        }
        
        return true;
    }
    
    /**
     * Unlocks the specified project by removing the project lock file.
     *
     * Returns true on succeess, else throws exception if existing lock cannot be removed.
     *
     * @param string $project the project name
     *
     * @return bool
     */
    public static function unlockProject($project) {
        if (!$project) {
            throw new Exception('Null project');
        }
        Util::writeLog('ida', 'unlockProject: project=' . $project, \OCP\Util::DEBUG);
        $lockFilePathname = self::buildLockFilePathname($project);
        if (self::projectIsLocked($project, $lockFilePathname)) {
            if (!unlink($lockFilePathname)) {
                throw new Exception('Failed to delete lock file for project ' . $project);
            }
        }
        
        return true;
    }
    
    /**
     * Builds and returns the full pathname of the lock file for the specified project.
     *
     * @param string $project the project name
     *
     * @return string
     */
    protected static function buildLockFilePathname($project) {
        $dataRootPathname = '/mnt/storage_vol01/ida'; // TODO get this from configuration
        if ($project === 'all') {
            $lockFilePathname = $dataRootPathname . '/LOCK';
        }
        else {
            $lockFilePathname = $dataRootPathname . '/' . Constants::PROJECT_USER_PREFIX . $project . '/files/LOCK';
        }
        Util::writeLog('ida', 'buildLockFilePathname: lockFilePathname=' . $lockFilePathname, \OCP\Util::DEBUG);
        
        return ($lockFilePathname);
    }
    
}
