/*
	Copyright 2011-2012 Fundació per a la Universitat Oberta de Catalunya

	This file is part of PeLP (Programming eLearning Plaform).

    PeLP is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PeLP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
package edu.uoc.pelp.services;

import edu.uoc.pelp.model.vo.admin.PelpActiveSubjects;
import edu.uoc.pelp.model.vo.admin.PelpLanguages;

/**
 * PeLP Administration Services interface class
 * @author Xavier Baró
 */
//@WebService(serviceName = "AdminService")
public interface AdminService {
    
    /**
     * Adds a new administrator. Only super administators can perform this action
     * @param userName Username of new administrator
     * @return True if the user is successfully added or False otherwise
     */
    boolean addAdministrator(String userName);
    
    /**
     * Remove an administrator. Only super administators can perform this action
     * @param userName Username of administrator to be removed
     * @return True if the user is successfully removed or False otherwise
     */
    boolean deleteAdministrator(String userName);
    
    PelpActiveSubjects[] getActiveSubjects();
    
    PelpActiveSubjects[] getActiveSubjects(String semester);
    
    boolean addActiveSubject(String semester,String subject);
    
    boolean removeActiveSubject(String semester, String subject);
    
    boolean setActiveSubject();
    
    boolean setActiveSemester(String semesterID, boolean status);
        
    boolean addLanguage(String code,String description);
    
    boolean removeLanguage(String code);
    
    PelpLanguages[] getLanguages();
    
    boolean setLanguage(String code,String description);
}
