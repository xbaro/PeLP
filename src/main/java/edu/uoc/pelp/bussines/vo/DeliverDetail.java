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
package edu.uoc.pelp.bussines.vo;

/**
 * Detailed information for a user deliver
 * @author Xavier Baró
 */
public class DeliverDetail extends DeliverSummary {
    /**
     * Deliver files
     */
    private DeliverFile[] _deliverFiles;  
    
    /**
     * Tests results
     */
    private TestResult[] _testResults;

    /**
     * Default constructor from parent object
     */
    public DeliverDetail(DeliverSummary deliverSummary) {
        super(deliverSummary);
    }

    public DeliverFile[] getDeliverFiles() {
        return _deliverFiles;
    }

    public void setDeliverFiles(DeliverFile[] _deliverFiles) {
        this._deliverFiles = _deliverFiles;
    }

    public TestResult[] getTestResults() {
        return _testResults;
    }

    public void setTestResults(TestResult[] _testResults) {
        this._testResults = _testResults;
    }
    
    
}
