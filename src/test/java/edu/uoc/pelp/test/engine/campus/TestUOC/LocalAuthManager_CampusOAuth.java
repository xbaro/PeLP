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
package edu.uoc.pelp.test.engine.campus.TestUOC;

import edu.uoc.pelp.engine.campus.*;
import edu.uoc.pelp.engine.campus.UOC.CampusConnection;
import edu.uoc.pelp.engine.campus.UOC.SubjectID;
import edu.uoc.pelp.exception.AuthPelpException;
import org.junit.Assert;
import org.junit.Test;

/**
 * Perform all tests over the Authorization module of the PeLP platform.
 * This class uses the local campus connection with an authenticated user,
 * which does not have access to any subject.
 * @author Xavier Baró
 */
public class LocalAuthManager_CampusOAuth {
    
    private ICampusConnection _campusConnection=(ICampusConnection) new CampusConnection();
    
    
    public LocalAuthManager_CampusOAuth() {
        // Set a test token
        String token="2c3b70b2-8390-49c5-8249-0f8842da1d28";
        _campusConnection=new CampusConnection(token);
    }
    
    @Test 
    public void testGetUserData() throws AuthPelpException {
        // Check that user is not authenticated
        Person person=_campusConnection.getUserData();
        Assert.assertNotNull(person);
    }
    
    @Test 
    public void testGetUserSubjects() throws AuthPelpException {
        // Check that user is not authenticated
        SubjectID[] subjects=(SubjectID[]) _campusConnection.getUserSubjects(null);
        Assert.assertNotNull(subjects);
    }
    
}
