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

import edu.uoc.pelp.bussines.vo.Activity;
import edu.uoc.pelp.bussines.vo.DeliverDetail;
import edu.uoc.pelp.bussines.vo.UserInformation;
import edu.uoc.pelp.services.vo.SubjectData;

/**
 * PeLP Services interface class
 * @author Xavier Baró
 */
public interface PelpService {
    /**
     * Get the information for current user
     * @param campusSession Campus session
     * @return User information object
     */
    
    public UserInformation getUserInformation(String campusSession);
    
    /**
     * Get the active subjects for current user
     * @param campusSession Campus session
     * @return List of subjects
     */
    public SubjectData[] getUserSujects(String campusSession);
    
    /**
     * Get the actvities for a certain subject
     * @param campusSession Campus session
     * @param subjectID Subject identifier
     * @return 
     */
    public Activity[] getSubjectActivities(String campusSession,String subjectID);
    
    /**
     * Compile given code and pass the given tests.
     * @param campusSession Campus session (can be null if user is not authenticated)
     * @param code Code to be processed
     * @param progLanguage Identifier for programming language
     * @param tests Array of tests to be passed by the code (optional)
     * @return Object with all the results from this process
     */
    //public DeliverReport compileCode(String campusSession,String code,String progLanguage,Test[] tests);
    
    /**
     * Add a new deliver of current user for given activity
     * @param campusSession Campus session
     * @param activity Activity object
     * @param files Files to be delivered
     * @return Result for new added deliver.
     */
    //public DeliverDetail addDeliver(String campusSession,Activity activity, DeliverFile[] files);
    
    /**
     * Get all the delivers of current user for given activity
     * @param campusSession Campus session
     * @param activity Activity object
     * @return List of results.
     */
    public DeliverDetail[] getDelivers(String campusSession,Activity activity);
}
