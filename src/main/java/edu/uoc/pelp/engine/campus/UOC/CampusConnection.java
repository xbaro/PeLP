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
package edu.uoc.pelp.engine.campus.UOC;

import edu.uoc.pelp.engine.campus.*;
import edu.uoc.pelp.exception.AuthPelpException;

/**
 * Implements the campus access for the Universitat Oberta de Catalunya (UOC).
 * @author Xavier Baró
 */
public class CampusConnection implements ICampusConnection{

    private String sesion;
    private UserID userID;

    private String aplicacioTren;
    private String appIdTREN;
    private String appId;

    public CampusConnection() {
        
    }

    public CampusConnection(String sesion) {
            super();
            this.sesion = sesion;
    }

    @Override
    public boolean isUserAuthenticated() throws AuthPelpException {
         throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public IUserID getUserID() throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }


    @Override
    public ISubjectID[] getUserSubjects(ITimePeriod timePeriod) throws AuthPelpException {
        return getUserSubjects(null, timePeriod); 
    }

    @Override
    public ISubjectID[] getUserSubjects(UserRoles userRole, ITimePeriod timePeriod) throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public IClassroomID[] getUserClassrooms(ISubjectID subjectID) throws AuthPelpException {    
        return getUserClassrooms(null, subjectID);
    }

    @Override
    public IClassroomID[] getUserClassrooms(UserRoles userRole, ISubjectID subjectID) throws AuthPelpException {
	throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public IClassroomID[] getSubjectClassrooms(ISubjectID subject, UserRoles userRole) throws AuthPelpException {
        return getUserClassrooms(userRole, subject);
    }

    @Override
    public boolean isRole(UserRoles role, ISubjectID subject, IUserID user) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean isRole(UserRoles role, ISubjectID subject) throws AuthPelpException {
        return isRole(role,subject,getUserID());
    }

    @Override
    public boolean isRole(UserRoles role, IClassroomID classroom, IUserID user) throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean isRole(UserRoles role, IClassroomID classroom) throws AuthPelpException {
        boolean encontrado = false;
        IClassroomID[] classrooms = getUserClassrooms(role, null);
        for (IClassroomID iclassroomID : classrooms) {
            ClassroomID classroomID = (ClassroomID) iclassroomID;
            if( classroomID.compareTo(classroom) == 0){
                encontrado = true;
                break;
            }
        }
        return encontrado;
    }

    @Override
    public IUserID[] getRolePersons(UserRoles role, ISubjectID subject) throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public IUserID[] getRolePersons(UserRoles role, IClassroomID classroom) throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean hasLabSubjects(ISubjectID subject) throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public ISubjectID[] getLabSubjects(ISubjectID subject) throws AuthPelpException {
        //TODO: Una solucio es utilitzar la taula PELP_MainLabSubjects, amb les correspondencies
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean hasEquivalentSubjects(ISubjectID subject) throws AuthPelpException {
        return getEquivalentSubjects(subject).length > 0;
    }

    @Override
    public ISubjectID[] getEquivalentSubjects(ISubjectID subject) throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean isCampusConnection() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public Subject getSubjectData(ISubjectID isubjectID) throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public Classroom getClassroomData(IClassroomID classroomID) throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public Person getUserData(IUserID userID) throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public Person getUserData() throws AuthPelpException {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public ITimePeriod[] getPeriods() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public ITimePeriod[] getActivePeriods() {
        throw new UnsupportedOperationException("Not supported yet.");
    }
}
