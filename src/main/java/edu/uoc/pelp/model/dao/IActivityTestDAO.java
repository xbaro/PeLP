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
package edu.uoc.pelp.model.dao;

import edu.uoc.pelp.engine.activity.ActivityID;
import edu.uoc.pelp.engine.activity.ActivityTest;
import edu.uoc.pelp.engine.activity.TestID;
import java.util.List;

/**
 * This interface defines the basic operations of the DAO for activities
 * @author Xavier Baró
 */
public interface IActivityTestDAO {
    /**
     * Adds a new test to the given activity
     * @param activityID Identifier of the activity
     * @param object Object to be stored
     * @return The identifier for new object or null if an error occurred
     */
    TestID add(ActivityID activityID,ActivityTest object);
    
    /**
     * Deletes the given object
     * @param id Identifier of the object to be deleted
     * @return True if the process finish successfully or Fals if any error occurred. It fails if the object does not exist.
     */
    boolean delete(TestID id);
    
    /**
     * Update the stored object with the new object
     * @param object Object to be updated
     * @return True if the process finish successfully or Fals if any error occurred. It fails if the object does not exist.
     */
    boolean update(ActivityTest object);
    
    /**
     * Obtain the list of all tests
     * @return List of Tests
     */
    List<ActivityTest> findAll();
    
    /**
     * Obtain the list of all tests for the given activity
     * @param activity Activity identifier
     * @return List of Activities
     */
    List<ActivityTest> findAll(ActivityID activity);
    
    /**
     * Find the information of an activity test
     * @param id The identifier of the object to be searched
     * @return Object with all the information or null if not exists.
     */
    ActivityTest find(TestID id);
}
