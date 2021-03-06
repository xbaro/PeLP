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

import edu.uoc.pelp.engine.campus.IPelpID;
import edu.uoc.pelp.engine.campus.IUserID;

/**
 * Implementation for the user identifier in the campus of the Universitat Oberta de Catalunya
 * @author Xavier Baró
 */
public class UserID implements IUserID {
    
    /**
     * Users are identified by their id value. 
     */
    public String idp = null;
    
    public UserID(String idp) {
        this.idp=idp;
    }
    
    public int compareTo(IUserID userID) {
        String strUserID=((UserID)userID).idp;
        
        // Try to delegate NULL users to the end of sorted lists
        if(idp==null) {      
            if(strUserID==null) {
                return 0;
            } else {
                return 1;
            }
        }
        
        return idp.compareTo(strUserID);
    }

    protected void copyData(IPelpID genericID) {
        idp=((UserID)genericID).idp;
    }

    public int compareTo(IPelpID id) {
        return idp.compareTo(((UserID)id).idp);
    }

    public IPelpID parse(String str) {
        if(str==null) {
            return null;
        }
        return new UserID(str);
    }

    @Override
    public String toString() {
        return  idp;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final UserID other = (UserID) obj;
        if ((this.idp == null) ? (other.idp != null) : !this.idp.equals(other.idp)) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 7;
        hash = 73 * hash + (this.idp != null ? this.idp.hashCode() : 0);
        return hash;
    }
    
    
}
