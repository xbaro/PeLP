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
package edu.uoc.pelp.services.vo;

/**
 * Subject information for UOC subjects
 * @author Xavier Baró
 */
public class SubjectData {
        
    /**
     * Subject identifier
     */
    protected String _subjectID;
    
    /**
     * Short description for the subject
     */
    protected String _shortName;
    
    /**
     * Full description of the subject
     */
    protected String _description;
    
    /**
     * Subject code
     */
    protected String _subjectCode;
    
    /**
     * Semester code
     */
    protected String _semesterCode;
        
    public SubjectData() {
        super();
    }

    public String getDescription() {
        return _description;
    }

    public void setDescription(String _description) {
        this._description = _description;
    }

    public String getSemesterCode() {
        return _semesterCode;
    }

    public void setSemesterCode(String _semesterCode) {
        this._semesterCode = _semesterCode;
    }

    public String getShortName() {
        return _shortName;
    }

    public void setShortName(String _shortName) {
        this._shortName = _shortName;
    }

    public String getSubjectCode() {
        return _subjectCode;
    }

    public void setSubjectCode(String _subjectCode) {
        this._subjectCode = _subjectCode;
    }

    public String getSubjectID() {
        return _subjectID;
    }

    public void setSubjectID(String _subjectID) {
        this._subjectID = _subjectID;
    }

    
}
