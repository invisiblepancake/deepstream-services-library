/*
The MIT License

Copyright (c) 2024, Prominence AI, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in-
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

#ifndef _DSL_GST_BINTR_BINTR_H
#define _DSL_GST_BINTR_BINTR_H

#include "Dsl.h"
#include "DslApi.h"
#include "DslElementr.h"
#include "DslBintr.h"

namespace DSL
{
    /**
     * @brief convenience macros for shared pointer abstraction
     */
    #define DSL_GST_BINTR_PTR std::shared_ptr<GstBintr>
    #define DSL_GST_BINTR_NEW(name) \
        std::shared_ptr<GstBintr>(new GstBintr(name))
        
    class GstBintr : public Bintr
    {
    public: 
    
        /**
         * @brief Ctor for the GstBintr class - i.e. custom Pipeline component.
         * @param[in] name unique name to give to the .
        */
        GstBintr(const char* name);

        /**
         * @brief dtor for the GstBintr class.
         */
        ~GstBintr();

        /**
         * @brief Adds the GstBintr to a Parent Branch Bintr.
         * @param pParentBintr Parent Branch to add this Bintr to.
        */
        bool AddToParent(DSL_BASE_PTR pParentBintr);

        /**
         * @brief Adds a Child Element to this Bintr.
         * @param pChild Child Element to add this Bintr to.
        */
        bool AddChild(DSL_ELEMENT_PTR pChild);
    
        /**
         * @brief Removes a Child Element from this Bintr.
         * @param pChild Child Element to add this Bintr to.
        */
        bool AddChild(DSL_ELEMENT_PTR pChild);
 
        /**
         * @brief Links all Child Elementrs owned by this Bintr.
         * @return true if all links were succesful, false otherwise.
         */
        bool LinkAll();
        
        /**
         * @brief Unlinks all Child Elementrs owned by this Bintr.
         * Calling UnlinkAll when in an unlinked state has no effect.
         */
        void UnlinkAll();
    
    private:

        /**
         * @brief Index variable to incremment/assign on Element add.
         */
        uint m_nextElementIndex;
        
        /**
         * @brief Map of child Elementrs for this GstBintr.
         * indexed by thier add-order for execution.
         */
        std::map <uint, DSL_ELEMENT_PTR> m_pElementrsIndexed;
        
        /**
         * @brief Map of child Elementrs for this GstBintr.
         * indexed by thier add-order, added when linked.
         */
        std::map <uint, DSL_ELEMENT_PTR> m_pElementrsLinked;
    };
 
} 
#endif // _DSL_GST_BINTR_BINTR_H
