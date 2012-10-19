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

import edu.uoc.pelp.bussines.vo.Subject;

/**
 * Services interface class
 * @author Xavier Baró
 */
public interface PelpService {
    /**
     * Get the active subjects for current user
     * @param campusSession Campus session
     * @return List of subjects
     */
    public Subject[] getUserSujects(String campusSession);
    
    /**
     * Add a new deliver of current user for given activity
     * @param campusSession Campus session
     * @param activity Activity object
     * @param files Files to be delivered
     * @return Result for new added deliver.
     */
   // public DeliverDetail addDeliver(String campusSession,Activity activity, DeliverFile[] files);
    
    /**
     * Get all the delivers of current user for given activity
     * @param campusSession Campus session
     * @param activity Activity object
     * @return List of results.
     */
   // public DeliverDetail[] getDelivers(String campusSession,Activity activity);
}
